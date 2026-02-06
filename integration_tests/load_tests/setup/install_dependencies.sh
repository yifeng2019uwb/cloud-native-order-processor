#!/bin/bash
# Load Test Dependencies Installation
# Separate from frequent integration tests - only runs when load tests are executed

echo "🚀 Load Test Dependencies Setup"
echo "================================"

# Check if k6 is already installed
if command -v k6 &> /dev/null; then
    echo "✅ k6 is already installed: $(k6 version)"
    exit 0
fi

echo "📦 Installing k6..."

# Detect OS and install k6
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - use Homebrew
    if command -v brew &> /dev/null; then
        echo "Installing k6 via Homebrew..."
        brew install k6
        if [ $? -eq 0 ]; then
            echo "✅ k6 installed successfully"
            k6 version
            exit 0
        else
            echo "❌ Failed to install k6 via Homebrew"
            exit 1
        fi
    else
        echo "❌ Homebrew not found. Please install k6 manually:"
        echo "   brew install k6"
        echo "   OR visit: https://k6.io/docs/getting-started/installation/"
        exit 1
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux - use package manager or download binary
    if command -v apt-get &> /dev/null; then
        echo "Installing k6 via apt..."
        sudo gpg -k
        sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
        echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
        sudo apt-get update
        sudo apt-get install k6
        if [ $? -eq 0 ]; then
            echo "✅ k6 installed successfully"
            k6 version
            exit 0
        else
            echo "❌ Failed to install k6 via apt"
            exit 1
        fi
    elif command -v yum &> /dev/null; then
        echo "Installing k6 via yum..."
        sudo yum install https://dl.k6.io/rpm/repo.rpm
        sudo yum install k6
        if [ $? -eq 0 ]; then
            echo "✅ k6 installed successfully"
            k6 version
            exit 0
        else
            echo "❌ Failed to install k6 via yum"
            exit 1
        fi
    else
        echo "⚠️  Package manager not found. Please install k6 manually:"
        echo "   Visit: https://k6.io/docs/getting-started/installation/"
        exit 1
    fi
else
    echo "❌ Unsupported OS: $OSTYPE"
    echo "Please install k6 manually: https://k6.io/docs/getting-started/installation/"
    exit 1
fi
