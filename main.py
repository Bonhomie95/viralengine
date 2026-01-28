from config.settings import get_settings
from engine.discovery.youtube_fetcher import YouTubeFetcher
from engine.discovery.twitch_fetcher import TwitchFetcher
from engine.discovery.discovery import DiscoveryService
from engine.scheduler.runner import run_forever


def main() -> None:
    print("🚀 AI Shorts Engine Starting...")

    s = get_settings()

    yt = YouTubeFetcher(
        api_key=s.youtube_api_key,
        user_agent=s.user_agent,
    )

    tw = TwitchFetcher(
        client_id=s.twitch_client_id,
        client_secret=s.twitch_client_secret,
        user_agent=s.user_agent,
    )

    discovery = DiscoveryService(
        yt=yt,
        tw=tw,
        days_lookback=s.days_lookback,
        max_results_per_creator=s.max_results_per_creator,
    )

    try:
        run_forever(discovery, "config/creators.json")
    except KeyboardInterrupt:
        print("\n🛑 Scheduler stopped by user.")
    except Exception as e:
        print(f"❌ Fatal error: {e}")


if __name__ == "__main__":
    main()
