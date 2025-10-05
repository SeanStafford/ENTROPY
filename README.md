```
                                        /
╔══════════════════════════════════^══/═════════════════════════════════╗
║                                 / \/                                  ║
║  ███████╗ ███╗   ██╗ █████^██╗ /█████╗   ██████╗  ██████╗  ██╗   ██╗  ║
║  ██╔════╝ ████╗  ██║ ╚══█/╔\═╝/██╔══██╗ ██╔═══██╗ ██╔══██╗ ╚██╗ ██╔╝  ║
║  █████╗   ██╔██╗ ██║ ^  /█║ \/ ██████╔╝ ██║   ██║ ██████╔╝  ╚████╔╝   ║
║  ██╔══╝   ██║╚██╗██║/ \/██║    ██╔══██╗ ██║   ██║ ██╔═══╝    ╚██╔╝    ║
║  ███████╗ ██║ ╚████/    ██║    ██║  ██║ ╚██████╔╝ ██║         ██║     ║
║  ╚══════╝ ╚═╝  ╚══/╝    ╚═╝    ╚═╝  ╚═╝  ╚═════╝  ╚═╝         ╚═╝     ║
╚═══════════════════════════════════════════════════════════════════════╝
```

## Installation

```bash
# Install base dependencies
make install

# For development (includes testing and evaluation tools)
make install-dev

```


## Project Organization

```
ENTROPY/
├── Makefile                
├── README.md               
├── pyproject.toml          
├── banner.txt              
├── configs/
├── data/
│   ├── raw/               
│   └── processed/         
├── entropy/
│   ├── contexts/          
│   │   ├── market_data/   # Stock prices and signals
│   │   ├── news_analysis/ # News processing
│   │   ├── retrieval/     # RAG implementations
│   │   └── generation/    # LLM response synthesis
│   ├── prototype/       
│   ├── evaluation/       
│   └── utils/            
├── notebooks/
└── outs/
```

## Architecture

ENTROPY follows domain-driven design principles, organizing code around financial analysis contexts:

- **Market Data Context**: Handles quantitative stock information
- **News Analysis Context**: Processes qualitative information from news articles
- **Retrieval Context**: Implements RAG
- **Generation Context**: Manages generation

## Formatting

```bash
# Format code
make format

# Check linting
make lint

# Clean cache files
make clean

```