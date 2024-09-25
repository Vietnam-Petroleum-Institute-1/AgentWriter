import PropTypes from "prop-types";

// Hàm để xác định hình đại diện cho từng loại file
const getFileIcon = (type) => {
  if (type.startsWith("image/")) {
    return "🖼️"; // Biểu tượng cho ảnh
  } else if (type.startsWith("application/pdf")) {
    return "📄"; // Biểu tượng cho PDF
  } else {
    return "📁"; // Biểu tượng cho file khác
  }
};

const FileList = ({ files }) => {
  if (!files || !Array.isArray(files)) {
    return null; // Nếu files không hợp lệ, không render gì
  }

  return (
    <div className="p-4 border-2 border-green-500 rounded-lg shadow-md mt-4 bg-black">
      <h2 className="text-xl font-semibold mb-4">Uploaded Files</h2>

      <ul>
        {files.map((file, index) => (
          <div
            key={index}
            className="border-2 border-blue-500 rounded-full flex items-center w-full h-24 p-2" // Đặt chiều rộng thành 100% của lớp cha
          >
            <div className="flex items-center">
              {/* Thay thế icon.type bằng biểu tượng thực tế, đây chỉ là ví dụ */}
              <span className="material-icons mr-2">
                {getFileIcon(file.type)}
              </span>{" "}
              {/* Icon ở bên trái */}
            </div>
            <p className="flex-grow text-center text-sm truncate">
              {file.name}
            </p>{" "}
            {/* Tên file ở giữa */}
          </div>
        ))}
      </ul>
    </div>
  );
};

// Xác thực kiểu dữ liệu của props
FileList.propTypes = {
  files: PropTypes.arrayOf(PropTypes.object).isRequired, // files là một mảng các đối tượng và là bắt buộc
};

export default FileList;
