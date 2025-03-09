# Run two things:
# 1. python run_socket.py
# 2. cd website && python -m http.server 8080

# Run 1. python run_socket.py

python guess-note/run_socket.py & python_pid=$!

# Run 2. cd website && python -m http.server 8080
cd guess-note/website && python -m http.server 8000 & http_server_pid=$!

# Wait for both processes to finish
wait $python_pid $http_server_pid
