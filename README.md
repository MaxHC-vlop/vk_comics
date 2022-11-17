# Vk comics

Posts a random comic taken from [xkcd](https://xkcd.com/), in your VK group.

## How to install

- Сlone this repository:
```bash
git clone git@github.com:MaxHC-vlop/vk_comics.git
```

 - You must have python3.9 (or higher) installed .

 - Create a virtual environment on directory project:
 ```bash
python3 -m venv env
 ```
- Start the virtual environment:
```bash
. env/bin/activate
```
- Then use pip to install dependencies:
```bash
pip install -r requirements.txt
```
- Create a file in the project directory `.env` :
```bash
touch .env
```

- Create variables in `.env` file :

[API key here](https://dev.vk.com/api/access-token/implicit-flow-user)

[Group ID here](https://regvk.com/id/)
```
GROUP_ID='your_croup_id'

VK_TOKEN='your_vk_token'
```
## Run

```bash
python3 main.py
```