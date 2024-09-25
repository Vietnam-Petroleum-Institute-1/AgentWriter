// import { useState } from "react"; // Chỉ cần khai báo một lần
import "./App.css";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import SignIn from "./components/SignIn/SignIn";
import Home from "./components/Home";
import Chatbot from "./components/Chatbot/Chatbot";
// import UploadFile from "./components/UploadFile/UploadFile"; // Sửa đường dẫn nếu cần
// import FileList from "./components/FileList/FileList";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />{" "}
        <Route path="/signin" element={<SignIn />} />
        <Route path="/chatbot" element={<Chatbot />} />
      </Routes>
    </Router>
  );
};

export default App;

{
  /* <h1>File Upload Example</h1>
<UploadFile onFileUpload={handleFileUpload} />
<div className="uploaded-files">
  <FileList files={files} /> {/* Gọi FileList và truyền files */
}

// const [files, setFiles] = useState([]); // Khai báo state cho file

// const handleFileUpload = (uploadedFiles) => {
//   setFiles((prevFiles) => [...prevFiles, ...uploadedFiles]);
// };
