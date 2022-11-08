from typing_extensions import dataclass_transform
import replicate
import anchorpoint, apsync
import requests, time, os

# DO NOT SHARE. Sign up n replicate.com and go to Account "API token"
REPLICATE_API_TOKEN = "a36406..."

ctx = anchorpoint.Context.instance()

def predict(prompt: str):
    os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

    progress = anchorpoint.Progress("Running Stable Diffusion", show_loading_screen=True)

    # Start Stable Diffusion on Replicate servers
    model = replicate.models.get("stability-ai/stable-diffusion")
    output_url = model.predict(prompt=prompt)[0]

    # Create a random image name 
    current_time = int(round(time.time() * 1000))
    path = os.path.join(ctx.path, str(current_time) + ".png")

    # Download result
    r = requests.get(output_url, stream = True)
    if r.status_code == 200:
        with open(path, 'wb') as f:
            for chunk in r:
                f.write(chunk)

    # Tell Anchorpoint what the prompt was
    apsync.set_attribute_text(path, "Prompt", prompt)

def generate(d):
    # Get the prompt from the user input
    prompt = d.get_value("prompt")

    # Run the prediction
    ctx.run_async(predict, prompt)
    
    d.close()

d = anchorpoint.Dialog()
d.title = "Stable Diffusion Text to Image"
d.add_text("Prompt:").add_input(placeholder="electric sheep, neon, synthwave", var="prompt", width=400)
d.add_info("This is running <b>Stable Diffusion</b> on <a href=\"wwwreplicate.com\">replicate.com</a>")
d.add_button("Generate Image", callback=generate)
d.show()