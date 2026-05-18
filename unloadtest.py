import requests

def get_loaded_models():
    """Get currently loaded models"""
    url = "http://localhost:1234/api/v1/models"
    headers = {"Content-Type": "application/json"}
    
    response = requests.get(url)
    return response.json()

def unload_model(instance_id):
    """Unload a specific model"""
    url = "http://localhost:1234/api/v1/models/unload"
    headers = {"Content-Type": "application/json"}
    payload = {"instance_id": instance_id}
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def unload_all():
    """Get loaded models and unload them"""
    data = get_loaded_models()
    models = data.get("models", [])
    
    loaded = []
    for model in models:
        instances = model.get("loaded_instances", [])
        if instances:  # Only if there are loaded instances
            for instance in instances:
                instance_id = instance.get("id")
                loaded.append(instance_id)
                print(f"Unloading: {instance_id}")
                result = unload_model(instance_id)
                print(result)
    
    if not loaded:
        print("No models currently loaded")

# Usage
unload_all()