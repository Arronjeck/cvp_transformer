import os
import yaml
import json
from langchain.llms.base import LLM
from langchain_community.llms.chatglm3 import ChatGLM3
from transformers import AutoTokenizer, AutoModel, AutoConfig
from typing import List, Dict, Optional, Any


# 参考 ChatGLM3 实现 LLM 接口
class ChatGLM36B(LLM):    
    model_name: str = "THUDM/chatglm3-6b"
    max_token: int = 8192
    do_sample: bool = False
    temperature: float = 0.8
    top_p = 0.8
    tokenizer: object = None
    model: object = None
    history: List = []
    tool_names: List = []
    has_search: bool = False
    model_name: object = None
    model_config: object = None
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {**super()._identifying_params, "model_name": self.model_name}
    
    def __init__(self, model_name):        
        super().__init__()
        self.model_name = model_name
        self.model_config = AutoConfig.from_pretrained(
            model_name,
            trust_remote_code=True
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True
        )
        self.model = AutoModel.from_pretrained(
            model_name, config=self.model_config, trust_remote_code=True, device_map="auto"
        ).cuda().eval()
        
    @property
    def _llm_type(self) -> str:
        return "chat_glm_3"
    
    def tool_config_from_file(tool_name, directory="/root/knowledge_base_v2/models/Tool"):
        """search tool yaml and return json format"""
        for filename in os.listdir(directory):
            if filename.endswith('.yaml') and tool_name in filename:
                file_path = os.path.join(directory, filename)
                with open(file_path, encoding='utf-8') as f:
                    return yaml.safe_load(f)
        return None

    def _tool_history(self, prompt: str):
        ans = []
        tool_prompts = prompt.split(
            "You have access to the following tools:\n\n")[0].split("\n\nUse a json blob")[0].split("\n")

        tool_names = [tool.split(":")[0] for tool in tool_prompts]
        self.tool_names = tool_names
        tools_json = []
        for i, tool in enumerate(tool_names):
            tool_config = self.tool_config_from_file(tool)
            if tool_config:
                tools_json.append(tool_config)
            else:
                ValueError(
                    f"Tool {tool} config not found! It's description is {tool_prompts[i]}"
                )

        ans.append({
            "role": "system",
            "content": "Answer the following questions as best as you can. You have access to the following tools:",
            "tools": tools_json
        })
        query = f"""{prompt.split("Human: ")[-1].strip()}"""
        return ans, query

    def _extract_observation(self, prompt: str):
        return_json = prompt.split("Observation: ")[-1].split("\nThought:")[0]
        self.history.append({
            "role": "observation",
            "content": return_json
        })
        return

    def _extract_tool(self):
        if len(self.history[-1]["metadata"]) > 0:
            metadata = self.history[-1]["metadata"]
            content = self.history[-1]["content"]
            if "tool_call" in content:
                for tool in self.tool_names:
                    if tool in metadata:
                        input_para = content.split("='")[-1].split("'")[0]
                        action_json = {
                            "action": tool,
                            "action_input": input_para
                        }
                        self.has_search = True
                        return f"""
Action: 
```
{json.dumps(action_json, ensure_ascii=False)}
```"""
        final_answer_json = {
            "action": "Final Answer",
            "action_input": self.history[-1]["content"]
        }
        self.has_search = False
        return f"""
Action: 
```
{json.dumps(final_answer_json, ensure_ascii=False)}
```"""

    def _call(self, prompt: str, history: List = [], stop: Optional[List[str]] = ["<|user|>"]):
        print("======")
        print(prompt)
        print("======")
        if not self.has_search:
            self.history, query = self._tool_history(prompt)
        else:
            self._extract_observation(prompt)
            query = ""
        # print("======")
        # print(history)
        # print("======")
        _, self.history = self.model.chat(
            self.tokenizer,
            query,
            history=self.history,
            do_sample=self.do_sample,
            max_length=self.max_token,
            temperature=self.temperature,
        )
        response = self._extract_tool()
        history.append((prompt, response))
        return response