# A trading bot for 2 to 1 engulfing

## Install Dependencies

```Bash
pip install -r requirements.txt
```

## Setup your API_KEY and SECRET

Put your API_KEY and SECRET in a new **.env** file.

Example:

```Bash
API_KEY=<YOUR_API_KEY>
SECRET=<YOUR_SECRET>
```

## Deploy

```Bash
crontab -e
*/30  * * * * bash <repo_path>/run.sh >> <repo_path>/log.txt 2>&1
```

<repo_path> is the path where you cloned the repository.

## Backtest Results

![Return](./figures/return.png)