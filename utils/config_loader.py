import yaml

class ConfigLoader:
    def __init__(self, config_path='config.yaml'):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        with open(self.config_path, "r", encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    
    def save_config(self):
        with open(self.config_path, "w", encoding='utf-8') as f:
            yaml.dump(self.config, f)
            
    def get_config(self):
        return self.config
    
    
CONFIGER = ConfigLoader(config_path='config/config.yaml')

def sample_function():
    config = CONFIGER.get_config()
    print(config)
    config['OpenAIModel']['OPENAI_API_KEY']='xxxxxxx'
    CONFIGER.save_config()
    
sample_function()