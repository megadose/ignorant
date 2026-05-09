# Ignorant
Message from the original creator @megadose:
> 👋 Hi there! For any professional inquiries or collaborations, please reach out to me at:
> megadose@protonmail.com
> 
> 📧 Preferably, use your professional email for correspondence. Let's keep it short and sweet, and all in English!
> #### For BTC Donations : 1FHDM49QfZX6pJmhjLE5tB2K6CaTLMZpXZ
> ### ignorant does not alert the target phone number
> ignorant allows you to check if a phone number is used on different sites like snapchat, instagram.
> 
> ![](https://github.com/megadose/gif-demo/raw/master/ignorant-demo.gif)

## Ignorant-ng
All the intelligence lies with megadose. I'm merely a code inspector bringing the code up to standard. 

@ArcherHeffern's contribution
- Modernizes to uv for easier onboarding
- Adds types to codebase
- Makes extending easier 

## 💡 Prerequisite
[Python 3.14](https://www.python.org/downloads/release/python-370/)

## 🛠️ Installation
### With PyPI

```pip3 install ignorant-ng```

### With Github

```bash
git clone https://github.com/archerheffern/ignorant.git
cd ignorant/
uv run main.py 
```

## 📚 Example

```bash
uv run main.py 33 644637111
```


### Rate limit, just change your IP

## Extending
Add a new file and class in src.modules extending Module, and implementing the run method.

```python
# ./ignorant/src/modules/new_website.py
from typing import final

from httpx import AsyncClient
from src.module import Module, ModuleResult

@final
class NewWebsite(Module):
    async def run(
        self,
        phone: str,
        country_code: str,
        client: AsyncClient,
    ) -> ModuleResult:
        raise NotImplementedError()
```


## Thank you to :
- [megadose](https://github.com/megadose)
- [yazeed44](https://github.com/yazeed44)

## 📝 License
[GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.fr.html)
