import discord
import asyncio
from binance.client import Client
from datetime import datetime, timedelta

# Discord Bot Setup
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
client = discord.Client(intents=intents)
discord_token = 'MTEzNTIwNDgyNDY5OTM4Nzk3NA.GbSzKR.x6WFlkzb1vBjTxs5FPkciNJb5ySvTRm3C3xzMw'

# Define the send_alert function
async def send_alert(message):
    channel = client.get_channel(1140236323928674357)  # Replace CHANNEL_ID with your actual channel ID
    await channel.send(message)

# Binance API Setup
binance_api_key = 'iQHDvkZdJBCAAyvqdXjZUyjyk12u92J7spt2euC6XgZb9pUNVPTBCC5Mb1ykaeM2'
binance_api_secret = '29K8c1ykmpEQxq1CuSb3FD2cKBHuBrnVToK9dR0h5lo1lWHkCsFbrKtTVUOOjB0u'
binance_client = Client(binance_api_key, binance_api_secret)

# Define a function to get the current price of a token
def get_current_price(symbol):
    ticker = binance_client.get_ticker(symbol=symbol)
    return float(ticker['lastPrice'])

async def check_volume_surges():
    while True:
        try:
            tickers = binance_client.get_ticker()
            usdt_pairs = [ticker for ticker in tickers if ticker['symbol'].endswith("USDT")]
            usdt_pairs_sorted_by_volume = sorted(usdt_pairs, key=lambda x: float(x['volume']), reverse=True)[:50]
            
            for ticker in usdt_pairs_sorted_by_volume:
                symbol = ticker['symbol']

                price_change_percent = float(ticker['priceChangePercent'])
                if price_change_percent > 0:
                    klines = binance_client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_15MINUTE, limit=4)  # Fetch 4 candles
                    if len(klines) == 4:
                        volume_candles = [float(kline[5]) for kline in klines]
                        buy_volume = volume_candles[-1] - volume_candles[-2]  # Calculate buy volume in the last 15 Minutes

                        if buy_volume <= 0:
                            continue  # Skip this ticker if there's no buying volume

                        volume_change = (buy_volume / volume_candles[-2]) * 100  # Calculate volume change based on buy volume
                        if volume_change > 0:
                            try:
                                current_price = get_current_price(symbol)
                                message = f"{symbol} volume pumped {volume_change:.2f}% with ${buy_volume:.2f} buy in the last 15 Minutes and current price is ${current_price:.7f}"
                            except Exception as e:
                                message = f"{symbol} volume pumped {volume_change:.2f}% with ${buy_volume:.2f} buy in the last 15 Minutes and could not retrieve current price."
                                print(f"Error retrieving current price for {symbol}: {e}")
                            await send_alert(message)
            
            await asyncio.sleep(300)  # Check every 5 minutes

        except KeyError as e:
            print("KeyError:", e)
        except Exception as e:
            print("Error:", e)

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

    # Start checking volume surges
    client.loop.create_task(check_volume_surges())

client.run(discord_token)