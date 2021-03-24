# Ignorant
#### For BTC Donations : 1FHDM49QfZX6pJmhjLE5tB2K6CaTLMZpXZ
### ignorant does not alert the target email
ignorant allows you to check if a phone number is used on different sites like snapchat, instagram.

![](https://github.com/megadose/gif-demo/raw/master/ignorant-demo.gif)
## 💡 Prerequisite
[Python 3](https://www.python.org/downloads/release/python-370/)

## 🛠️ Installation
### With PyPI

```pip3 install ignorant```

### With Github

```bash
git clone https://github.com/megadose/ignorant.git
cd ignorant/
python3 setup.py install
```

## 📚 Example

```bash
ignorant 33 644637111
```


### Rate limit, just change your IP

## 📈 Example of use

```python
import trio
import httpx

from ignorant.modules.shopping.amazon import amazon


async def main():
    phone="644637111"
    country_code="33"
    client = httpx.AsyncClient()
    out = []

    await amazon(phone, country_code, client, out)

    print(out)
    await client.aclose()

trio.run(main)
```


## The output of the modules
The result of the modules is in this form : ```{"name": "instagram","domain":"instagram.com","method":"orther","frequent_rate_limit":"False","rateLimit": False,"exists": False}```
- rateLitmit : is to find out if you've been rate-limited
- exists : know an account is associated with the mail

## Thank you to :
- [social-media-detector-api](https://github.com/yazeed44/social-media-detector-api)

## 📝 License

[GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.fr.html)

## Modules :
| name                | domain                                 | method            | frequent_rate_limit |
| ------------------- | -------------------------------------- | ----------------- | ------------------- |
| amazon              | amazon.com                             | login             |     ✘               |
| instagram           | instagram.com                          | register          |     ✘               |
| snapchat            | snapchat.com                           | register          |     ✘               |
