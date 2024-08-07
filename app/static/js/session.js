function checkOrCreateSession(user_id, session_id) {
    console.log("Checking or creating session");
    showWaitingBubble();
    return fetch("/api/session_exist", {
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
          return getConversation(user_id, session_id); // Return the promise from getConversation
        } else if (data.result === 0) {
          const start_time = new Date().toISOString();
          const end_time = new Date(Date.now() + 60 * 60 * 1000).toISOString();
          return createSession(user_id, session_id, start_time, end_time);
        } else {
          document.getElementById("chatMessages").innerHTML =
            '<div class="message bot"><div class="message-content">Vui lòng đăng nhập để sử dụng trợ lý ảo</div></div>';
          const chatInput = document.querySelector(".chat-input");
          if (chatInput) {
            chatInput.style.display = "none";
          }
        }
      })
      .catch((error) => {
        console.error("Error in checkOrCreateSession:", error);
        throw error;
      })
      .finally(() => {
        hideWaitingBubble();
      });
  }
  
  function createSession(user_id, session_id, start_time, end_time) {
    console.log("Creating session");
    showWaitingBubble();
    return fetch("/api/session", {
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
        return startConversation(user_id, session_id); // Return the promise from startConversation
      })
      .catch((error) => {
        console.error("Error in createSession:", error);
        throw error;
      })
      .finally(() => {
        hideWaitingBubble();
      });
  }
  
  function startConversation(user_id, session_id) {
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
  
        const userInput = document.getElementById("userInput");
        const sendButton = document.getElementById("sendButton");
        if (userInput && sendButton) {
          userInput.disabled = false;
          sendButton.disabled = false;
        }
  
        isConversationStarted = true; // Set flag to true once conversation is started
        console.log("Conversation started, conversation_id:", conversation_id);
  
        // // Gửi tin nhắn tự động
        addMessageToChat("bot", "Xin chào, rất vui được hỗ trợ bạn");
  
        return conversation_id;
      })
      .catch((error) => {
        console.error("Error in startConversation:", error);
        document.getElementById("chatMessages").innerHTML +=
          '<div class="message bot"><div class="message-content">Sorry, something went wrong while starting the conversation.</div></div>';
        throw error;
      })
      .finally(() => {
        hideWaitingBubble();
      });
  }
  
  function getConversation(user_id, session_id) {
    console.log("Getting conversation");
    showWaitingBubble();
    return fetch("/api/conversation_id", {
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
  
        const userInput = document.getElementById("userInput");
        const sendButton = document.getElementById("sendButton");
        if (userInput && sendButton) {
          userInput.disabled = false;
          sendButton.disabled = false;
        }
  
        isConversationStarted = true; // Set flag to true once conversation ID is obtained
        return data.result;
      })
      .catch((error) => {
        console.error("Error in getConversation:", error);
        throw error;
      })
      .finally(() => {
        hideWaitingBubble();
      });
  }
  