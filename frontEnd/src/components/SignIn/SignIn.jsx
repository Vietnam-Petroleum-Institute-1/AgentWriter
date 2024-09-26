import { useState, useEffect } from "react";

const SignIn = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [token, setToken] = useState("");
  const backHost = "http://localhost:5000"; // Include the protocol

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const urlToken = params.get("token");

    if (urlToken) {
      console.log("Token found in URL:", urlToken);
      setToken(urlToken); // Store the token in state
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    // Call the Flask API to check token or authenticate
    const response = await fetch(`${backHost}/api/check_token`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token: token, username, password }), // Include token in the request
    });

    if (response.ok) {
      const data = await response.json();
      console.log(data);

      // Assuming the response contains session_id and user_id
      const { session_id, user_id } = data;

      // Set cookies in the browser
      // document.cookie = `session_id=${session_id}; path=/; max-age=${60 * 60}`; // 1 hour
      // document.cookie = `user_id=${user_id}; path=/; max-age=${60 * 60}`; // 1 hour
      // window.location.href = "/chatbot"; // Redirect to chatbot page
    } else {
      const data = await response.json();
      setError(data.error || "Authentication failed");
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Username</label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
      </div>
      <div>
        <label>Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>
      {error && <p style={{ color: "red" }}>{error}</p>}{" "}
      {/* Styled error message */}
      <button type="submit">Sign In</button>
    </form>
  );
};

export default SignIn;
