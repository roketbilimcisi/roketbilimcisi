# calculator_logic.py
import math

class CalculatorLogic:
    def __init__(self):
        self.current_expression = ""
        self.history = []  # Store as: (internal_expression, display_expression, result_string)
        self.degree_mode = True # True for Degree, False for Radian
        self.second_function_active = False # For "2nd" key functionality

    def toggle_degree_mode(self):
        self.degree_mode = not self.degree_mode
        return "DEG" if self.degree_mode else "RAD"

    def toggle_second_function_mode(self):
        self.second_function_active = not self.second_function_active
        # Return value not currently used by UI directly, but good for debugging
        return "2nd Active" if self.second_function_active else "2nd Inactive"

    def _handle_implicit_multiplication(self, func_name):
        # Add * if a number/constant/closing_paren is followed by a function name or opening_paren
        if self.current_expression and \
           (self.current_expression[-1].isdigit() or \
            self.current_expression.endswith("math.pi") or \
            self.current_expression.endswith("math.e") or \
            self.current_expression.endswith(")")):
            
            # Check if func_name is a function that needs multiplication before it
            # Exclude operators, constants being added directly, or explicit power ^
            if func_name not in ["pi", "e", "^", "x!", "%", ")", "mod", "pow"]: # "pow" becomes ^
                # Further exclude 2nd functions that replace existing ones (like sin to asin)
                # or functions that are more like operators (like "square" which becomes ^(2))
                is_replacing_function = self.second_function_active and \
                                         func_name in ["sin", "cos", "tan", "log", "ln", "sqrt"]
                is_operator_like = func_name in ["square", "reciprocal", "percentage"]
                
                if not (is_replacing_function or is_operator_like):
                    self.current_expression += "*"


    def input_digit(self, digit):
        if self.current_expression == "0" and digit != ".":
            self.current_expression = ""
        # Allow π3 -> π*3 or e3 -> e*3 only if previous was constant, not end of function
        elif self.current_expression and \
             (self.current_expression.endswith("math.pi") or self.current_expression.endswith("math.e")) and \
             (digit.isdigit() or digit == "."): # Also handle π. becoming π*.
            self.current_expression += "*"
        self.current_expression += str(digit)

    def input_operator(self, operator):
        # Handle implicit multiplication for constants like π or e followed by an operator like (
        if self.current_expression and \
           (self.current_expression.endswith("math.pi") or self.current_expression.endswith("math.e")) and \
           operator == "(":
             self.current_expression += "*"

        if self.current_expression:
            last_char = self.current_expression[-1]
            # Allow '-' after '(', or any operator.
            if last_char in "+-*/^%(": # Added % for modulo
                if operator == "-" and last_char in "(+-*/^%": 
                    self.current_expression += operator
                # Prevent double operators like ++, **, %%, unless it's a valid sequence e.g. 5*(-2)
                # or if the new operator is '(' e.g. 5*(
                elif operator not in "+-*/^%" or last_char == "(":
                    self.current_expression += operator
                # Else: if last is operator and new is operator (not '-' or '('), replace or ignore
                # For simplicity, current behavior is mostly to append or handle via specific logic
            else: # Last char is a number or )
                self.current_expression += operator
        elif operator in ["-", "(", "%"]: # Allow expression to start with negative, parenthesis, or modulo
            self.current_expression += operator
        # Do not add operator if expression is empty and it's not '-' or '(' or '%'
        elif not self.current_expression and operator not in ["-", "(", "%"]:
            return


    def input_function(self, func_name):
        self._handle_implicit_multiplication(func_name)
        
        if self.second_function_active:
            if func_name == "sin": self.current_expression += "math.asin("
            elif func_name == "cos": self.current_expression += "math.acos("
            elif func_name == "tan": self.current_expression += "math.atan("
            elif func_name == "log": self.current_expression += "math.pow(10," # For 10^x
            elif func_name == "ln": self.current_expression += "math.exp("    # For e^x
            elif func_name == "sqrt": self.current_expression += "^(2)"       # For x^2 (square)
            else: # If no 2nd version, use primary or it's a non-2nd function like 'pi' or '('
                self._input_primary_function(func_name)
        else: # Primary functions
            self._input_primary_function(func_name)

    def _input_primary_function(self, func_name):
        if func_name == "pow": # xʸ button
            self.input_operator("^") # Use operator logic for ^
        elif func_name == "sqrt":
            self.current_expression += "math.sqrt("
        elif func_name == "log": # log10
            self.current_expression += "math.log10("
        elif func_name == "ln": # doğal logaritma
            self.current_expression += "math.log("
        elif func_name in ["sin", "cos", "tan"]:
            # Degree mode conversion is handled inside eval for display simplicity
            # but internally we can prepare it if needed or rely on get_current_expression_display
            if self.degree_mode:
                self.current_expression += f"math.{func_name}(math.radians("
            else:
                self.current_expression += f"math.{func_name}("
        elif func_name == "pi":
            # Implicit multiplication for "digit<pi>" or ")<pi>"
            if self.current_expression and (self.current_expression[-1].isdigit() or self.current_expression.endswith(")")):
                self.current_expression += "*"
            self.current_expression += "math.pi"
        elif func_name == "e":
            if self.current_expression and (self.current_expression[-1].isdigit() or self.current_expression.endswith(")")):
                self.current_expression += "*"
            self.current_expression += "math.e"
        elif func_name == "(":
             self.current_expression += "("
        elif func_name == ")":
             self.current_expression += ")"
        elif func_name == "1/x": # Reciprocal
            # This should ideally encapsulate the last number or expression
            # For simplicity, we append ^(-1)
            # A more robust way would be to parse and transform the expression
            if self.current_expression:
                 self.current_expression += "^(-1)"
            else: # Start with 1/
                self.current_expression += "(1/" # Or just "1/" and expect user to complete
        elif func_name == "x!": # Factorial
            self.current_expression += "math.factorial("
        elif func_name == "percentage": # Percentage button (called from simple and advanced)
            # This will append /100. The calculation context (e.g., A + B%) is complex.
            if self.current_expression and (self.current_expression[-1].isdigit() or self.current_expression[-1] == ')'):
                self.current_expression += "/100"
            # else: behavior if expression is empty or ends with operator? Maybe add "0/100" or ignore.
        elif func_name == "mod": # Modulo button from advanced mode
            self.input_operator("%") # Use the operator logic for "%"

    def clear_all(self): 
        self.current_expression = ""
        self.second_function_active = False # Reset 2nd mode on AC

    def clear_entry(self): 
        self.current_expression = ""
        # self.second_function_active = False # Optionally reset on C as well

    def delete_last(self):
        if self.current_expression:
            # Define patterns for functions and constants to delete them whole
            # Longer patterns first to avoid partial deletions
            patterns = [
                "math.asin(math.radians(", "math.acos(math.radians(", "math.atan(math.radians(", # Should not happen
                "math.sin(math.radians(", "math.cos(math.radians(", "math.tan(math.radians(",
                "math.asin(", "math.acos(", "math.atan(",
                "math.sin(", "math.cos(", "math.tan(",
                "math.log10(", "math.log(", "math.sqrt(",
                "math.factorial(", "math.pow(10,", "math.exp(",
                "math.pi", "math.e",
                "^(2)", "^(-1)" # For x² and 1/x
            ]
            deleted_complex = False
            for p in patterns:
                if self.current_expression.endswith(p):
                    self.current_expression = self.current_expression[:-len(p)]
                    deleted_complex = True
                    break
            if not deleted_complex:
                self.current_expression = self.current_expression[:-1]

    def calculate(self):
        if not self.current_expression:
            return ""

        internal_expr_for_history = self.current_expression
        display_expr_for_history = self.get_current_expression_display() 

        expression_to_eval = str(self.current_expression) # Make a copy
        expression_to_eval = expression_to_eval.replace("^", "**")
        
        # Auto-close parentheses
        open_brackets = expression_to_eval.count("(")
        close_brackets = expression_to_eval.count(")")
        expression_to_eval += ")" * (open_brackets - close_brackets)
        
        try:
            # Güvenli eval ortamı
            allowed_globals = {"math": math, "__builtins__": {}}
            # Allow all functions from math module
            for name in dir(math):
                if callable(getattr(math, name)) and not name.startswith("_"):
                    allowed_globals[name] = getattr(math, name)
            # Also allow constants pi and e to be used if typed directly (though input adds math.pi)
            allowed_globals["pi"] = math.pi 
            allowed_globals["e"] = math.e

            result = eval(expression_to_eval, allowed_globals, {})

            # Formatting the result
            if isinstance(result, float) and abs(result) < 1e-12 and result != 0: result = 0.0 
            if isinstance(result, float) and result.is_integer(): result = int(result)

            history_entry = (internal_expr_for_history, display_expr_for_history, str(result))
            self.history.append(history_entry)
            if len(self.history) > 30: self.history.pop(0)

            self.current_expression = str(result) # Update current_expression AFTER saving history
            return str(result)
        except ZeroDivisionError:
            self.current_expression = ""
            return "Sıfıra Bölme Hatası"
        except (SyntaxError, TypeError, NameError, ValueError, OverflowError) as e:
            error_message = "Hata"
            if "invalid syntax" in str(e).lower(): error_message = "Geçersiz İfade"
            elif "factorial() not defined for negative values" in str(e).lower(): error_message = "Negatif Faktöriyel Yok"
            elif "factorial() argument must be an integer" in str(e).lower(): error_message = "Faktöriyel İçin Tamsayı"
            elif "out of range" in str(e).lower() or "overflow" in str(e).lower(): error_message = "Sınır Aşıldı"
            elif "math domain error" in str(e).lower(): error_message = "Tanım Kümesi Hatası"
            elif "modulo by zero" in str(e).lower(): error_message = "Mod Sıfıra Bölme"
            self.current_expression = ""
            return error_message

    def get_history_text(self): # Compatible with new history format
        return [f"{disp_exp} = {res}" for _internal_exp, disp_exp, res in reversed(self.history)]

    def get_current_expression_display(self):
        text = str(self.current_expression) # Work with a copy
        
        # Define replacements: longer patterns first
        # For degree mode, eval handles math.sin(math.radians(value))
        # For display, we want to show sin(value)
        # For inverse functions, math.degrees(math.asin(value)) becomes asin(value) in display
        
        replacements = {}
        if self.degree_mode:
            replacements.update({
                "math.asin(": "asin(",  # No math.radians for input to asin
                "math.acos(": "acos(",
                "math.atan(": "atan(",
                "math.sin(math.radians(": "sin(",
                "math.cos(math.radians(": "cos(",
                "math.tan(math.radians(": "tan(",
            })
        else: # Radian mode
            replacements.update({
                "math.asin(": "asinR(",
                "math.acos(": "acosR(",
                "math.atan(": "atanR(",
                "math.sin(": "sinR(",
                "math.cos(": "cosR(",
                "math.tan(": "tanR(",
            })

        replacements.update({
            "math.log10(": "log(",
            "math.log(": "ln(",
            "math.sqrt(": "√(",
            "math.factorial(": "fact(",
            "math.pow(10,": "10^(", # Display for 10^x
            "math.exp(": "e^(",    # Display for e^x
            "math.pi": "π",
            "math.e": "e",
            "**(2)": "²",          # Display for x^2 (internal might be ^(2))
            "^(-1)": "⁻¹",         # Display for 1/x
            "**": "^"              # General power operator
            # '%' (modulo) should display as is
        })

        for internal, display in replacements.items():
            text = text.replace(internal, display)
        
        # Special handling for ^(2) if it wasn't caught by **(2)
        if text.endswith("^(2)"): text = text[:-3] + "²"
        if text.endswith("^(-1)"): text = text[:-4] + "⁻¹"
            
        return text