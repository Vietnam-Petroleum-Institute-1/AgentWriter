import { useState, useEffect } from "react";

const Chatbot = () => {
  const [isConversationStarted, setIsConversationStarted] = useState(false);
  const [isWaitingForBot, setIsWaitingForBot] = useState(false);
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState("");
  const [fileInput, setFileInput] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [feedbackMessageId, setFeedbackMessageId] = useState(null);

  useEffect(() => {
    // Check for user_id and session_id from cookies
    const user_id = getCookie("user_id");
    const session_id = getCookie("session_id");

    console.log("User ID:", user_id, "Session ID:", session_id);

    if (user_id && session_id) {
      // Check if user exists
      fetch("/api/user_exist", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_id }),
      })
        .then((response) => response.json())
        .then((data) => {
          console.log("User existence check:", data);
          if (data.result) {
            checkOrCreateSession(user_id, session_id);
            loadTranscripts(user_id, session_id); // Load transcripts if session_id exists
          } else {
            addMessageToChat("bot", "Vui lòng đăng nhập để sử dụng trợ lý ảo");
            hideChatInput();
          }
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    } else {
      addMessageToChat("bot", "Vui lòng đăng nhập để sử dụng trợ lý ảo");
      hideChatInput();
    }
  }, []);

  const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
    return null;
  };

  const checkOrCreateSession = (user_id, session_id) => {
    console.log("Checking or creating session");
    showWaitingBubble();
    fetch("/api/session_exist", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ user_id, session_id }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Session existence check:", data);
        if (data.result === 1) {
          document.getElementById("chatContainer").style.display = "flex";
          return getConversation(user_id, session_id);
        } else if (data.result === 0) {
          const start_time = new Date().toISOString();
          const end_time = new Date(Date.now() + 60).toISOString();
          return createSession(user_id, session_id, start_time, end_time);
        } else {
          addMessageToChat("bot", "Vui lòng đăng nhập để sử dụng trợ lý ảo");
          hideChatInput();
        }
      })
      .catch((error) => {
        console.error("Error in checkOrCreateSession:", error);
      })
      .finally(() => {
        hideWaitingBubble();
      });
  };

  const createSession = (user_id, session_id, start_time, end_time) => {
    console.log("Creating session");
    showWaitingBubble();
    fetch("/api/session", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ user_id, session_id, start_time, end_time }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Session creation result:", data);
        document.getElementById("chatContainer").style.display = "flex";
        return startConversation(user_id, session_id);
      })
      .catch((error) => {
        console.error("Error in createSession:", error);
      })
      .finally(() => {
        hideWaitingBubble();
      });
  };

  const startConversation = (user_id, session_id) => {
    console.log("Starting conversation");
    showWaitingBubble();
    return fetch("/api/start_conversation", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ user_id, session_id }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Start conversation result:", data);
        const conversation_id = data.conversation_id;
        sessionStorage.setItem("conversation_id", conversation_id);
        setIsConversationStarted(true);
        addMessageToChat(
          "bot",
          "Xin chào, tôi có thể giúp gì bạn?",
          data.message_id
        );
        return conversation_id;
      })
      .catch((error) => {
        console.error("Error in startConversation:", error);
      })
      .finally(() => {
        hideWaitingBubble();
      });
  };

  const getConversation = (user_id, session_id) => {
    console.log("Getting conversation");
    showWaitingBubble();
    fetch("/api/conversation_id", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ user_id, session_id }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Conversation ID:", data.result);
        sessionStorage.setItem("conversation_id", data.result);
        setIsConversationStarted(true);
        return data.result;
      })
      .catch((error) => {
        console.error("Error in getConversation:", error);
      })
      .finally(() => {
        hideWaitingBubble();
      });
  };

  const loadTranscripts = (user_id, session_id) => {
    console.log("Loading transcripts");
    fetch("/api/get_transcripts", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ user_id, session_id }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Transcripts data received:", data);
        let transcripts = data.transcripts;

        // Parse transcripts if it's a string
        if (typeof transcripts === "string") {
          try {
            transcripts = JSON.parse(transcripts);
          } catch (e) {
            console.error("Error parsing transcripts:", e);
            return;
          }
        }

        if (Array.isArray(transcripts) && Array.isArray(transcripts[0])) {
          transcripts = transcripts[0];
        }

        if (Array.isArray(transcripts)) {
          transcripts.forEach((transcript) => {
            if (Array.isArray(transcript)) {
              transcript.forEach((innerTranscript) => {
                if (innerTranscript && innerTranscript.role) {
                  const role = innerTranscript.role.toLowerCase();
                  if (innerTranscript.text !== "") {
                    addMessageToChat(
                      role,
                      innerTranscript.text,
                      innerTranscript.messageId || null
                    );
                  }
                } else {
                  console.warn(
                    "Transcript item missing role:",
                    innerTranscript
                  );
                }
              });
            } else if (transcript && transcript.role) {
              const role = transcript.role.toLowerCase();
              addMessageToChat(
                role,
                transcript.text,
                transcript.messageId || null
              );
            } else {
              console.warn("Transcript item missing role:", transcript);
            }
          });
        } else {
          console.error("Transcripts data is not in the expected format.");
        }
      })
      .catch((error) => {
        console.error("Error loading transcripts:", error);
      });
  };

  const handleKeyPress = (event) => {
    if (event.key === "Enter" && !isWaitingForBot && isConversationStarted) {
      sendMessage();
    }
  };

  const sendMessage = async () => {
    if (!isConversationStarted || isWaitingForBot) return;

    if (!userInput && fileInput.length === 0) {
      alert("Vui lòng nhập câu hỏi hoặc chọn file!");
      return;
    }

    const messageText = userInput.trim();
    if (messageText === "") return;

    addMessageToChat("user", messageText);
    setUserInput(""); // Clear input
    setIsWaitingForBot(true);

    try {
      const response = await fetch(`/api/message`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: messageText,
          user_id: getCookie("user_id"),
          session_id: getCookie("session_id"),
          conversation_id: conversationId,
          files: fileInput,
        }),
      });

      const data = await response.json();
      addMessageToChat("bot", data.result);
    } catch (error) {
      console.error("Error:", error);
      addMessageToChat(
        "bot",
        "Xin lỗi, tôi không đủ thông tin để trả lời câu hỏi này."
      );
    } finally {
      setIsWaitingForBot(false);
    }
  };

  const addMessageToChat = (sender, message, messageId = null) => {
    setMessages((prevMessages) => [
      ...prevMessages,
      { role: sender, text: message, messageId },
    ]);
  };

  const showWaitingBubble = () => {
    // Implement waiting bubble UI logic here
  };

  const hideWaitingBubble = () => {
    // Implement logic to hide waiting bubble here
  };

  const hideChatInput = () => {
    const chatInput = document.querySelector(".chat-input");
    if (chatInput) {
      chatInput.style.display = "none";
    }
  };

  return (
    <div className="flex justify-center items-center h-screen bg-gray-100">
      <div className="flex flex-col w-full max-w-md h-full bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="flex items-center bg-blue-600 text-white p-4 text-lg">
          <img
            src="/static/images/Logo_Petrovietnam.svg.png"
            alt="Logo"
            className="h-10 mr-3"
          />
          PVPower Assistant
        </div>
        <div className="flex-1 p-4 overflow-y-auto" id="chatMessages">
          {messages.map((msg, index) => (
            <div
              className={`mb-2 flex ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}
              key={index}
            >
              <div
                className={`max-w-[60%] p-2 rounded-lg shadow-md ${
                  msg.role === "user" ? "bg-blue-600 text-white" : "bg-gray-200"
                }`}
              >
                {msg.text}
              </div>
            </div>
          ))}
        </div>
        <div className="flex border-t">
          <input
            type="file"
            multiple
            onChange={(e) => setFileInput([...e.target.files])}
            className="p-4 border-none"
          />
          <input
            type="text"
            value={userInput}
            placeholder="Xin mời bạn hỏi..."
            onChange={(e) => setUserInput(e.target.value)}
            onKeyPress={handleKeyPress}
            className="flex-1 p-4 border-none outline-none text-lg"
            id="userInput"
          />
          <button
            onClick={sendMessage}
            className="p-4 bg-blue-600 text-white"
            id="sendButton"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;
