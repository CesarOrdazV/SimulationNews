from pathlib import Path

COMPETITOR_FEEDS = {
    "NVIDIA": [
        "https://blogs.nvidia.com/feed/",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCSKUoczbGAcMld7HjpCR8OA",
    ],
    "RoboDK": [
        "https://robodk.com/blog/feed/",
        "https://www.youtube.com/feeds/videos.xml?user=RoboDK",
    ],
    "Siemens Digital Industries": [
        "https://news.google.com/rss/search?q=siemens+digital+industries+simulation+digital+twin&hl=en&gl=US&ceid=US:en",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCYR5Kgzn6suihs56iJ8_vfw",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCaEEm-0s0x3MHg9jzFcHuQQ",
    ],
    "Visual Components": [
        "https://news.google.com/rss/search?q=%22visual+components%22+simulation+manufacturing&hl=en&gl=US&ceid=US:en",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UC-mCG6o3M7-U-INitjtLCXg",
    ],
    "Rockwell Automation": [
        "https://news.google.com/rss/search?q=rockwell+automation+emulate3d+digital+twin&hl=en&gl=US&ceid=US:en",
        "https://www.youtube.com/feeds/videos.xml?user=ROKAutomation",
        "https://www.emulate3d.com/feed/",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCIdH_v1UnEmeqA5Gl2zs7kA",
    ],
    "AnyLogic": [
        "https://news.google.com/rss/search?q=anylogic+simulation+digital+twin&hl=en&gl=US&ceid=US:en",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCdH-e29FvfphfWmI2EMZPhg",
    ],
    "F.EE / fescreen-sim": [
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCEUDfVb3q1VVyQubsAmwTPw",
    ],
}

BUSINESS_KEYWORD_FEEDS = {
    "Virtual Commissioning": [
        "https://news.google.com/rss/search?q=%22virtual+commissioning%22+manufacturing+automation&hl=en&gl=US&ceid=US:en",
    ],
    "Digital Twin Manufacturing": [
        "https://news.google.com/rss/search?q=%22digital+twin%22+manufacturing+simulation&hl=en&gl=US&ceid=US:en",
    ],
    "PLC Simulation": [
        "https://news.google.com/rss/search?q=plc+simulation+industrial+automation&hl=en&gl=US&ceid=US:en",
    ],
    "Robot Simulation": [
        "https://news.google.com/rss/search?q=robot+simulation+offline+programming+factory&hl=en&gl=US&ceid=US:en",
    ],
    "Intralogistics Simulation": [
        "https://news.google.com/rss/search?q=intralogistics+simulation+warehouse+automation&hl=en&gl=US&ceid=US:en",
    ],
}

KEYWORDS = [
    "virtual commissioning",
    "digital twin",
    "simulation",
    "factory",
    "robot",
    "robotics",
    "plc",
    "automation",
    "opc ua",
    "industrial",
    "intralogistics",
    "material handling",
    "tia portal",
    "omniverse",
]

SECTIONS = [
    ("business", "Business Keywords"),
    ("competitors", "Competitors"),
]

DATA_DIR = Path("data")
SEEN_FILE = DATA_DIR / "seen.json"
LATEST_BY_TOPIC_FILE = DATA_DIR / "latest_by_topic.json"
PAGES_DIR = Path("docs")
CSV_OUTPUT = Path("business_intelligence_brief.csv")
MARKDOWN_OUTPUT = Path("business_intelligence_brief.md")
HTML_OUTPUT = PAGES_DIR / "index.html"
