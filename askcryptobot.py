import os
from datetime import datetime
from pycoingecko import CoinGeckoAPI
from pathlib import Path
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


def get_crypto_dict(option_selected):
    cg = CoinGeckoAPI()
    coin_list = cg.get_coins_list()
    coin_id_symbol = {}
    coin_symbol_id = {}
    for each_item in coin_list:
        symbol = each_item["symbol"]
        id = each_item["id"]
        coin_id_symbol[id] = symbol
        coin_symbol_id[symbol] = id
    if option_selected == "id":
        return coin_id_symbol
    elif option_selected == "symbol":
        return coin_symbol_id
    else:
        return None


@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)


@app.event("app_mention")
def mention_handler(body, say):
    try:
        aLabel = body["event"]["blocks"][0]["elements"][0]["elements"][1][
            "text"
        ]
        label = aLabel.lower()
        label = label.strip(" \t\n\r")
        coin_dict = get_crypto_dict("symbol")
        if label in coin_dict:
            id = coin_dict[label]
        else:
            say(
                f"The coin:  {label} does not exist, please enter a valid coin"
            )
        say(
            f"For more info about {label}, please select from "
            f"the following options below"
        )
        say(
            blocks=[
                {
                    "type": "actions",
                    "block_id": "actions1",
                    "elements": [
                        {
                            "type": "static_select",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "What do you want to know?",
                            },
                            "action_id": "select_2",
                            "options": [
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Coin Description",
                                    },
                                    "value": "description",
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Coin Price",
                                    },
                                    "value": "price",
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Global Market Overview",
                                    },
                                    "value": "global",
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Trending Cryptocurrencies",
                                    },
                                    "value": "trending",
                                },
                            ],
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Go"},
                            "value": "Go",
                            "action_id": "button_click",
                        },
                    ],
                }
            ],
            text=f"{id}",
        )
    except IndexError:
        say(f"Ticker is missing, please enter a ticker. See example below:")
        say(f"```i.e. @askcryptobot btc```")
        return None


@app.action("select_2")
def handle_some_action(ack, body, logger):
    ack()
    logger.info(body)


@app.action("button_click")
def action_button_click2(body, ack, say):
    ack()
    cg = CoinGeckoAPI()
    coin_dict = get_crypto_dict("id")
    coin_symbol_id = get_crypto_dict("symbol")
    id = body["message"]["text"]
    input_selected = body["state"]["values"]["actions1"]["select_2"][
        "selected_option"
    ]["value"]
    if input_selected == "description":
        coin_info = cg.get_coin_by_id(id)
        say(f"```{coin_info['description']['en']}```")
    elif input_selected == "global":
        global_data = cg.get_global()
        updated_at = global_data["updated_at"]
        request_time = datetime.fromtimestamp(updated_at).strftime(
            "%m-%d-%y %H:%M:%S"
        )
        say(f"Crypto Market Overview - Last Updated at:  {request_time}")
        say(
            f"There are {global_data['active_cryptocurrencies']} "
            f"active cryptocurrencies."
        )
        say(
            f"The Market Cap Change Percentage in the last 24 hours:"
            f" {global_data['market_cap_change_percentage_24h_usd']:.2f}%."
        )
        say(f"Cryptocurrency Market Cap % (Top 10 cryptocurrencies)")
        top_mkt_cap_coins = global_data["market_cap_percentage"].items()
        top_ten = list(top_mkt_cap_coins)[:10]
        for each_cmc in top_ten:
            ticker = each_cmc[0]
            id = coin_symbol_id[ticker]
            coin_price_info = cg.get_price(id, vs_currencies="usd")
            for each_key in coin_price_info.keys():
                coin_price = coin_price_info[each_key]["usd"]
                say(
                    f"{coin_symbol_id[each_cmc[0]]:20}:  {each_cmc[0]:6}"
                    f" market cap is {each_cmc[1]:.2f}% of the total"
                    f" supply.  (USD) ${coin_price:.4f}"
                )
    elif input_selected == "price":
        coin_price_value = cg.get_price(id, vs_currencies="usd")
        for each_key in coin_price_value.keys():
            say(
                f"{each_key} ({coin_dict[each_key]}) is currently trading"
                f" at USD ${coin_price_value[each_key]['usd']}"
            )
    elif input_selected == "trending":
        coin_trends = cg.get_search_trending()
        say("These are the trending coins right now")
        for each_topic in coin_trends["coins"]:
            each_id = str(each_topic["item"]["name"])
            coin_price_value = cg.get_price(each_id, vs_currencies="usd")
            for each_key in coin_price_value.keys():
                say(
                    f"{each_key} ({coin_dict[each_key]}): "
                    f"Price in USD ${coin_price_value[each_key]['usd']}"
                )


@app.action("button_click3")
def action_button_click3(body, ack, say):
    ack()
    cg = CoinGeckoAPI()
    id = body["state"]["values"]["actions1"]["select_2"]["selected_option"][
        "value"
    ]
    coin_info = cg.get_coin_by_id(id)
    say(f"```{coin_info['description']['en']}```")


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
