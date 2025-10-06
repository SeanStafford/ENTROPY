import os
import sys
from pathlib import Path

import torch
from dotenv import load_dotenv
from openai import OpenAI
from transformers import AutoModelForCausalLM, AutoTokenizer

load_dotenv()


class LocalLLM:
    def __init__(self, model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        print(f"Loading {model_name}...")

        self.device = "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            dtype=torch.float32,
            low_cpu_mem_usage=True,
            device_map="cpu",
        )
        self.model.eval()

        print("Model loaded!\n")

    def generate(self, user_message: str, conversation_history: list[dict]) -> str:
        conversation_history.append({"role": "user", "content": user_message})

        prompt = self.tokenizer.apply_chat_template(
            conversation_history, tokenize=False, add_generation_prompt=True
        )

        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=256,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        response = self.tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[1] :], skip_special_tokens=True
        )

        conversation_history.append({"role": "assistant", "content": response})

        return response


class APIChat:
    def __init__(self, model: str = "gpt-4o-mini"):
        env_path = Path(__file__).parent.parent.parent / ".env"

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found.")

        self.client = OpenAI(api_key=api_key)
        self.model = model
        print(f"✓ Connected to OpenAI ({model})\n")

    def generate(self, user_message: str, conversation_history: list[dict]) -> str:
        conversation_history.append({"role": "user", "content": user_message})

        response = self.client.chat.completions.create(
            model=self.model, messages=conversation_history, temperature=0.7, max_tokens=512
        )

        assistant_message = response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": assistant_message})

        return assistant_message


def chat_loop(llm):
    mode = "Local CPU" if isinstance(llm, LocalLLM) else "API"
    print()
    print(f"ENTROPY Prototype Chat ({mode} Mode)")
    print()

    conversation_history = []

    while True:
        try:
            user_input = input("\n\033[1;34mYou:\033[0m ").strip()

            if not user_input:
                continue

            print("\nAssistant: ", end="", flush=True)
            response = llm.generate(user_input, conversation_history)
            print(response)

        except Exception as e:
            print(f"\n\033[1;31mError:\033[0m {e}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="ENTROPY Prototype Chat - Simple LLM chatbot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Use local TinyLlama model instead of OpenAI API (very slow on CPU)",
    )

    args = parser.parse_args()

    try:
        if args.local:
            print("⚠️  WARNING: Local mode is very slow on CPU!")
            llm = LocalLLM()
        else:
            llm = APIChat()

        chat_loop(llm)

    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\n\033[1;31mFatal error:\033[0m {e}")
        raise


if __name__ == "__main__":
    main()
