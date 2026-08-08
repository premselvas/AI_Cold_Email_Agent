import json
from groq import Groq
from config import Config

class CompanyResearch:
    """Agent that researches companies for cold email personalization."""
    
    def __init__(self):
        self.api_key = Config.GROQ_API_KEY
        self.model = Config.GROQ_MODEL
        if self.api_key and self.api_key != 'your_groq_api_key_here':
            self.client = Groq(api_key=self.api_key)
        else:
            self.client = None

    def research_company(self, company_name: str) -> dict:
        """Gather industry, mission, products, and technology stack information."""
        if not company_name:
            return self._default_info("Company")
            
        if self.client:
            try:
                prompt = f"""
Provide professional intelligence about the company "{company_name}".
Return a JSON object ONLY with the following exact keys:
"industry": (string),
"about": (short sentence summary),
"products": (list of up to 3 main products or services),
"technologies": (list of up to 5 technology keywords or focus areas)
"""
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a corporate intelligence agent. Output only valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)
            except Exception:
                pass
                
        return self._default_info(company_name)

    def _default_info(self, company_name: str) -> dict:
        return {
            "industry": "Technology & Services",
            "about": f"{company_name} is an innovative organization driving digital transformations and scalable solution development.",
            "products": ["Software Solutions", "Digital Products", "Cloud Services"],
            "technologies": ["Python", "Cloud Computing", "Data Analytics", "AI/ML", "REST APIs"]
        }
