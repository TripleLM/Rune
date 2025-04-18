"""
Button interface module for Rune
"""
import logging
import time
import threading
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    logging.warning("RPi.GPIO not available - button interface will be simulated")

logger = logging.getLogger("rune.interface.button")

class ButtonInterface:
    """Handles the push-to-talk button interface"""
    
    def __init__(self, config):
        """Initialize button interface with configuration"""
        self.config = config
        
        # Default GPIO pin for the push-to-talk button
        self.ptt_pin = config.get("ptt_pin", 17)
        
        # Set up GPIO
        self.setup_gpio()
        
        # Button press callback
        self.press_callback = None
        
        # Button state
        self.pressed = False
        
        # Start monitoring thread
        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_button)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        logger.info(f"ButtonInterface initialized with PTT pin {self.ptt_pin}")
    
    def setup_gpio(self):
        """Set up GPIO for button interface"""
        if not GPIO_AVAILABLE:
            logger.info("Running in simulation mode - GPIO not available")
            return
            
        try:
            # Set GPIO mode
            GPIO.setmode(GPIO.BCM)
            
            # Set up the push-to-talk button pin as input with pull-up resistor
            GPIO.setup(self.ptt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            
            logger.info("GPIO setup complete")
        except Exception as e:
            logger.error(f"Failed to set up GPIO: {e}")
            # Fall back to keyboard input for testing when not on a Raspberry Pi
            logger.info("Falling back to keyboard input simulation")
    
    def set_press_callback(self, callback):
        """
        Set callback function for button press
        
        Args:
            callback: Function to call when button is pressed
        """
        self.press_callback = callback
        logger.info("Button press callback registered")
    
    def monitor_button(self):
        """Monitor button state in background thread"""
        logger.info("Starting button monitoring thread")
        
        try:
            while self.running:
                if GPIO_AVAILABLE:
                    # Check if button is pressed (GPIO input is LOW when button is pressed)
                    button_state = GPIO.input(self.ptt_pin) == GPIO.LOW
                else:
                    # In simulation mode, just pretend the button is pressed every 10 seconds
                    time.sleep(10)
                    button_state = True
                
                # Button press detected
                if button_state and not self.pressed:
                    self.pressed = True
                    logger.info("Button pressed")
                    
                    # Call the registered callback
                    if self.press_callback:
                        try:
                            self.press_callback()
                        except Exception as e:
                            logger.error(f"Error in button press callback: {e}")
                
                # Button release detected
                elif not button_state and self.pressed:
                    self.pressed = False
                    logger.info("Button released")
                
                # Sleep to avoid busy-waiting
                time.sleep(0.01)
        except Exception as e:
            logger.error(f"Error in button monitoring thread: {e}")
        
        logger.info("Button monitoring thread stopped")
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up ButtonInterface resources")
        self.running = False
        
        # Clean up GPIO
        if GPIO_AVAILABLE:
            try:
                GPIO.cleanup(self.ptt_pin)
            except:
                pass 