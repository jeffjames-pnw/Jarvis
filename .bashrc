jarvis() {
  local msg="$*"
  curl -X POST "https://jarvis-ooow.onrender.com/chat" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d "{\"message\": \"$msg\"}"
}
