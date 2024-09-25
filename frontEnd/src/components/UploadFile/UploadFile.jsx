import PropTypes from "prop-types";
const UploadFile = ({ onFileUpload }) => {
  const handleFileChange = (event) => {
    const files = Array.from(event.target.files); // Chuyển đổi FileList thành mảng
    onFileUpload(files); // Gửi danh sách file lên component cha
  };

  return (
    <div>
      <input
        type="file"
        multiple // Cho phép chọn nhiều file
        onChange={handleFileChange}
      />
    </div>
  );
};

// Xác thực kiểu dữ liệu của props
UploadFile.propTypes = {
  onFileUpload: PropTypes.func.isRequired, // onFileUpload là một hàm và là bắt buộc
};

export default UploadFile;
