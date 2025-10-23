from prompts import FUNC_CALL_PROMPT



class FuncCall:
    def __init__(self):

        self.API_URL = "http://localhost:11434/api/generate"
        self.headers = {
            "Content-Type": "application/json"
        }

        self.prompt = FUNC_CALL_PROMPT

    def __query(self, payload):
        """
        Sends a payload to a TGI endpoint.
        """
        import requests
        response = requests.post(
            self.API_URL, headers=self.headers, json=payload)
        return response.json()

    def query_raven(self, user_query):
        """
        This function sends a request to the local Ollama endpoint to get Raven's function call.
        """
        output = self.__query(
            {
                "model": "nexusraven",  # 👈 required for Ollama API
                "prompt": self.prompt.format(query=user_query),
                "stream": False
            }
        )
    
        # Debug to inspect structure
        print("DEBUG OUTPUT:", output)
    
        # Some Ollama versions return {'response': '...'}
        if isinstance(output, dict):
            if "response" in output:
                text = output["response"]
            elif "generated_text" in output:
                text = output["generated_text"]
            else:
                raise ValueError(f"Unexpected output format: {output}")
    
        elif isinstance(output, list) and len(output) > 0:
            text = output[0].get("generated_text", "")
        else:
            raise ValueError(f"Unexpected output format: {output}")
    
        return text.replace("Call:", "").strip()



# QUESTION = "hi there"
# give_response_to_user(user_prompt='hi there')


# QUESTION = "what products are loans with interest rates of 10%?"
# filter_products(user_input_description='loans with interest rates of 10%')
# QUESTION = "recommend to me based on my historical behavior."
# recommend_product(user_id=get_user_id())
# QUESTION = "what of this products good for my business?"
# QUESTION = "hi there"

# funcall = FuncCall()
# raven_call = funcall.query_raven(QUESTION)

# print(f"Raven's Call: {raven_call}")
