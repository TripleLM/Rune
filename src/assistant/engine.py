"""
AI Assistant engine for Rune
"""
import logging
import os
from pathlib import Path

try:
    from ctransformers import AutoModelForCausalLM
    CTRANSFORMERS_AVAILABLE = True
except ImportError:
    CTRANSFORMERS_AVAILABLE = False
    logging.warning("ctransformers library not found. LLM inference will not work.")

logger = logging.getLogger("rune.assistant")

class AssistantEngine:
    """Core AI assistant engine that processes queries and generates responses"""
    
    def __init__(self, config):
        """Initialize assistant engine with configuration"""
        self.config = config["assistant"]
        
        # Get model configuration
        self.model_path = Path(self.config.get("model_path", "models/llm"))
        self.model_type = self.config.get("model_type", "local_llm")
        self.llm_model_name = self.config.get("llm_model_name", "mistral_7b")
        # Optional: Get specific model file if specified
        self.llm_model_file = self.config.get("llm_model_file") 
        
        # Initialize the local AI model
        self.model: AutoModelForCausalLM | None = None # Type hint for the loaded model object
        self.init_model()
        
        logger.info(f"AssistantEngine initialized for {self.model_type} / {self.llm_model_name} at {self.model_path}")
    
    def init_model(self):
        """Initialize the AI model based on configuration"""
        if self.model_type != "local_llm":
            logger.warning(f"Unsupported model type: {self.model_type}. Only 'local_llm' with ctransformers is implemented.")
            return
        
        if not CTRANSFORMERS_AVAILABLE:
            logger.error("Cannot initialize LLM: ctransformers library not installed.")
            return
            
        logger.info(f"Attempting to load {self.model_type} model '{self.llm_model_name}' from {self.model_path}")
        
        # Check if model path exists
        if not self.model_path.is_dir() and not self.model_path.is_file():
            logger.error(f"LLM model path not found: {self.model_path}. It should be a directory containing the model file or the model file itself.")
            # CTransformers might handle downloading if path is a HF repo ID, but we assume local path here.
            # You might need to create the directory: os.makedirs(self.model_path, exist_ok=True)
            return
            
        # Determine model file if not specified explicitly in config
        model_file_to_load = self.llm_model_file
        if not model_file_to_load:
             # Try to find a common GGUF file in the directory
             gguf_files = list(self.model_path.glob("*.gguf"))
             if len(gguf_files) == 1:
                 model_file_to_load = gguf_files[0].name
                 logger.info(f"Auto-detected model file: {model_file_to_load}")
             elif len(gguf_files) > 1:
                 logger.warning(f"Multiple .gguf files found in {self.model_path}. Specify 'llm_model_file' in config. Using the first one: {gguf_files[0].name}")
                 model_file_to_load = gguf_files[0].name
             else:
                 logger.error(f"No .gguf model file found in {self.model_path} and 'llm_model_file' not specified in config.")
                 return

        # Determine model type for ctransformers based on name
        ct_model_type = "mistral" # Default assumption for mistral_7b
        if "llama" in self.llm_model_name.lower():
            ct_model_type = "llama"
        # Add more mappings if needed (e.g., gemma, phi)
        
        try:
            # TODO: Make gpu_layers configurable
            self.model = AutoModelForCausalLM.from_pretrained(
                str(self.model_path), 
                model_file=model_file_to_load, 
                model_type=ct_model_type, 
                gpu_layers=50, # Number of layers to offload to GPU (0 for CPU only) - ADJUST AS NEEDED
                context_length=4096 # Example context length
            )
            logger.info("ctransformers LLM model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load ctransformers LLM model: {e}")
            self.model = None
    
    def process(self, query):
        """
        Process a user query and generate a response
        
        Args:
            query: Text query from user
            
        Returns:
            Assistant response text
        """
        logger.info(f"Processing query: {query}")
        
        if self.model:
            logger.info(f"Generating response using loaded model: {self.llm_model_name}")
            try:
                # TODO: Make generation parameters (max_new_tokens, temp, etc.) configurable
                # Simple prompt formatting - adjust as needed for your model
                prompt = f"User: {query}\nAssistant:"
                response_text = ""
                # Stream response for better perceived performance
                stream = self.model(prompt, stream=True, max_new_tokens=256, temperature=0.7, top_p=0.9)
                for token in stream:
                    print(token, end="", flush=True) # Print to console during generation
                    response_text += token
                print() # Newline after streaming
                
                logger.info(f"Generated response: {response_text}")
                return response_text.strip()
                
            except Exception as e:
                logger.error(f"Error during LLM inference: {e}")
                # Fallback to simple response if inference fails
        else:
            logger.warning("Cannot process query: Model not loaded.")

        # Simple keyword-based responses for demo if model not loaded/inference fails
        if "hello" in query.lower() or "hi" in query.lower():
            return "Hello! I'm Rune, your offline AI assistant. How can I help you today?"
        elif "time" in query.lower():
            import datetime
            now = datetime.datetime.now()
            return f"The current time is {now.strftime('%H:%M')}."
        elif "morse" in query.lower():
            return "I can interpret and generate Morse code. Would you like me to convert a message to Morse?"
        else:
            return "I'm an offline AI assistant running locally on this device. I'm here to help you with information and tasks while maintaining your privacy." 