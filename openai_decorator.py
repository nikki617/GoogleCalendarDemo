import inspect
import functools
import importlib.util

# Global variable to store all functions decorated with @openaifunc
openai_functions = []

# Map Python types to JSON schema types
type_mapping = {
    "int": "integer",
    "float": "number",
    "str": "string",
    "bool": "boolean",
    "list": "array",
    "tuple": "array",
    "dict": "object",
    "None": "null",
}

def get_type_mapping(param_type):
    param_type = param_type.replace("<class '", '').replace("'>", '')
    return type_mapping.get(param_type, "string")

def get_params_dict(params):
    params_dict = {}
    for k, v in params.items():
        annotation = str(v.annotation).split("[")
        param_type = annotation[0] if annotation else "string"
        array_type = annotation[1].strip("]") if len(annotation) > 1 else "string"
        
        param_type = get_type_mapping(param_type)
        params_dict[k] = {"type": param_type, "description": ""}
        if param_type == "array":
            array_type = get_type_mapping(array_type)
            params_dict[k]["items"] = {"type": array_type}
    return params_dict

def openaifunc(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    # Get function parameter information
    params = inspect.signature(func).parameters
    param_dict = get_params_dict(params)

    openai_functions.append({
        "name": func.__name__,
        "description": inspect.cleandoc(func.__doc__ or ""),
        "parameters": {
            "type": "object",
            "properties": param_dict,
            "required": list(param_dict.keys()),
        },
    })

    return wrapper

def get_openai_funcs():
    return openai_functions
