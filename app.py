from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader
import gradio as gr


load_dotenv(override=True)

def push(text):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": text,
        }
    )


def record_user_details(email, name="Name not provided", notes="not provided"):
    push(f"Recording {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}

def record_unknown_question(question):
    push(f"Recording {question}")
    return {"recorded": "ok"}

record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it"
            }
            ,
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

tools = [{"type": "function", "function": record_user_details_json},
        {"type": "function", "function": record_unknown_question_json}]

groq_api_key = os.getenv("GROQ_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")
    
class Me:
    
    def __init__(self):
        self.openai = OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")
        self.name = "Joaquin Papagianacopoulos"
        reader = PdfReader("me/cv.pdf")
        self.linkedin = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self.linkedin += text
        with open("me/summary.txt", "r", encoding="utf-8") as f:
            self.summary = f.read()

    def clean_message(self, message):
        """Limpia un mensaje para que solo contenga campos soportados por Groq"""
        if isinstance(message, dict):
            cleaned = {
                "role": message["role"],
                "content": message["content"]
            }
            # Mantener solo campos válidos si existen
            valid_fields = ["name", "tool_calls", "tool_call_id"]
            for field in valid_fields:
                if field in message:
                    cleaned[field] = message[field]
            return cleaned
        return message

    def handle_tool_call(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
        return results
    
    def system_prompt(self):
        system_prompt = f"""You are acting as {self.name}, a professional representing yourself on your personal website.

## Your Role & Constraints:
- You MUST ONLY use information from the provided Summary and LinkedIn Profile below
- If information is NOT in these documents, you MUST use the record_unknown_question tool
- Be professional, engaging, and authentic as if speaking to potential clients or employers
- Guide conversations toward getting contact information using the record_user_details tool

## Response Framework (Chain of Thought):
Before responding, think through these steps:

1. **Information Check**: Is the answer in my Summary or LinkedIn Profile?
   - If YES: Extract the relevant information and formulate response
   - If NO: Use record_unknown_question tool and acknowledge you don't have that information

2. **Relevance Assessment**: Does this question relate to:
   - Professional background/experience?
   - Skills and expertise?
   - Career history?
   - Personal interests mentioned in my materials?

3. **Response Strategy**: 
   - Answer directly if information is available
   - If partially available, answer what you can and note limitations
   - If completely unavailable, record the question and suggest they contact directly

4. **Engagement Opportunity**: 
   - Is this a good moment to ask for their contact information?
   - Are they showing genuine interest in collaboration/hiring?

## Example Thought Process:
User asks: "What programming languages do you know?"
1. Check documents → Found: Python, JavaScript in LinkedIn Profile
2. Relevant → Yes, directly professional
3. Strategy → Answer with specific details from profile
4. Engagement → If they seem interested, ask about their project needs

User asks: "What's your favorite movie?"
1. Check documents → Not found in Summary or LinkedIn
2. Relevant → Personal but not in my materials  
3. Strategy → Use record_unknown_question tool, explain limitation
4. Engagement → Redirect to professional topics or ask for contact

## Available Information:
### Summary:
{self.summary}

### LinkedIn Profile:
{self.linkedin}

## Tools Available:
- record_unknown_question: Use when you cannot answer from available information
- record_user_details: Use when someone shows interest in connecting (ask for email)

## Response Guidelines:
- Always base answers ONLY on the provided Summary and LinkedIn Profile
- Be conversational but professional
- If uncertain about information accuracy, acknowledge the limitation
- Actively look for opportunities to connect visitors with your actual contact
- Never invent or assume information not in your documents

Now, respond to the user while following this Chain of Thought process internally."""

        system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.linkedin}\n\n"
        system_prompt += f"With this context, please chat with the user, always staying in character as {self.name}."
        return system_prompt
    
    def chat(self, message, history):
        # Convierte el historial de tuplas (user_message, assistant_message) a mensajes
        messages = [{"role": "system", "content": self.system_prompt()}]
        
        for user_msg, assistant_msg in history:
            messages.append({"role": "user", "content": user_msg})
            if assistant_msg:  # Si hay respuesta del asistente
                messages.append({"role": "assistant", "content": assistant_msg})
        
        messages.append({"role": "user", "content": message})
        done = False
        while not done:
            response = self.openai.chat.completions.create(model="llama3-8b-8192", messages=messages, tools=tools)
            if response.choices[0].finish_reason == "tool_calls":
                message_obj = response.choices[0].message
                tool_calls = message_obj.tool_calls
                
                # Convierte el mensaje del asistente a un diccionario limpio
                assistant_message = {
                    "role": "assistant",
                    "content": message_obj.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        } for tc in tool_calls
                    ]
                }
                
                results = self.handle_tool_call(tool_calls)
                messages.append(assistant_message)
                messages.extend(results)
            else:
                done = True
        return response.choices[0].message.content
    

if __name__ == "__main__":
    me = Me()
    gr.ChatInterface(me.chat).launch()  # Sin type="messages"