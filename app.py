import os
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Nebius Token Factory client
client = OpenAI(
    base_url="https://api.tokenfactory.nebius.com/v1/",
    api_key=os.environ.get("NEBIUS_API_KEY")
)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>StackSmith — MACH Architecture Generator</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; background: #0a0a0a; color: #e0e0e0; }
        h1 { color: #76b900; }
        textarea { width: 100%; height: 120px; font-size: 16px; padding: 10px; background: #1a1a1a; color: #e0e0e0; border: 1px solid #333; border-radius: 6px; }
        button { padding: 12px 24px; font-size: 16px; background: #76b900; color: #000; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; }
        button:hover { background: #8fd600; }
        button:disabled { background: #333; color: #666; cursor: not-allowed; }
        #output { margin-top: 30px; white-space: pre-wrap; background: #1a1a1a; padding: 20px; border-radius: 8px; border: 1px solid #333; line-height: 1.6; }
        .badge { display: inline-block; background: #1a1a1a; color: #76b900; padding: 4px 10px; border-radius: 4px; font-size: 11px; margin-bottom: 10px; border: 1px solid #76b900; }
        .examples { margin: 15px 0; }
        .example-btn { background: #222; color: #76b900; border: 1px solid #76b900; padding: 6px 12px; margin-right: 8px; border-radius: 4px; cursor: pointer; font-size: 13px; }
        .example-btn:hover { background: #76b900; color: #000; }
    </style>
</head>
<body>
    <div class="badge">POWERED BY NVIDIA NEMOTRON 3 SUPER ON NEBIUS TOKEN FACTORY</div>
    <h1>StackSmith</h1>
    <p>Describe your business need. Get a headless/MACH architecture + integration code.</p>

    <div class="examples">
        <button class="example-btn" onclick="setExample('B2B wholesale platform with multi-currency, headless CMS, and PIM integration')">B2B Wholesale</button>
        <button class="example-btn" onclick="setExample('D2C fashion brand needing composable commerce with AR try-on and global CDN')">D2C Fashion</button>
        <button class="example-btn" onclick="setExample('Marketplace connecting local vendors with delivery logistics and real-time inventory')">Marketplace</button>
    </div>

    <textarea id="prompt" placeholder="e.g., I need a B2B commerce platform with multi-currency, headless CMS, and a PIM that integrates with Shopify Plus..."></textarea><br><br>
    <button onclick="generate()">Generate Stack</button>
    <div id="output"></div>

    <script>
        function setExample(text) {
            document.getElementById('prompt').value = text;
        }
        async function generate() {
            const btn = document.querySelector('button[onclick="generate()"]');
            btn.innerText = 'Generating...';
            btn.disabled = true;
            document.getElementById('output').innerText = 'Consulting Nemotron 3 Super on Nebius...';
            const res = await fetch('/generate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({prompt: document.getElementById('prompt').value})
            });
            const data = await res.json();
            document.getElementById('output').innerText = data.result;
            btn.innerText = 'Generate Stack';
            btn.disabled = false;
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/generate", methods=["POST"])
def generate():
    user_prompt = request.json.get("prompt", "")

    system_msg = """You are StackSmith, a senior solutions architect at a Global Systems Integrator specializing in MACH (Microservices, API-first, Cloud-native, Headless) and composable commerce architectures.

Given a business requirement, output exactly these sections:

1. RECOMMENDED STACK
List the specific tools/platforms with one-line descriptions (e.g., Contentful for CMS, commercetools for commerce, Vercel for frontend, Stripe for payments).

2. ARCHITECTURE OVERVIEW
Brief paragraph on how the pieces connect. Mention APIs, webhooks, or event-driven patterns where relevant.

3. INTEGRATION CODE
Provide a concrete, runnable code snippet. This could be:
- A Next.js API route
- A webhook handler
- A GraphQL query/mutation
- A deployment config (Docker, Terraform snippet)
Make it specific to the stack you recommended.

4. RATIONALE
Why this stack fits the requirement. Mention scalability, vendor flexibility, or time-to-market where relevant.

5. ESTIMATED COMPLEXITY
Low / Medium / High with a one-sentence justification.

Be specific. Avoid generic advice. If the user mentions a platform (e.g., Shopify Plus), incorporate it."""

    try:
        response = client.chat.completions.create(
            model="nvidia/nemotron-3-super-120b-a12b",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=2048
        )
        result = response.choices[0].message.content
    except Exception as e:
        result = f"Error: {str(e)}\n\nMake sure your NEBIUS_API_KEY is set and you have credits in your Token Factory account."

    return jsonify({"result": result})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
