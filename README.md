# MALGenAgent

  
    
## Mục lục
- [Tổng quan](#tổng-quan)
- [Kiến trúc MalGenAgent](#kiến-trúc-malgenagent) 
- [Cài đặt](#cài-đặt)
- [Hướng dẫn phát triển](#hướng-dẫn-phát-triển)
- [Lưu ý khi sử dụng MalGenAgent](#lưu-ý-khi-sử-dụng-malgenagent)
- [Lời kết](#lời-kết)
## Tổng quan
Trong bối cảnh các hình thức tấn công mã độc ngày càng phát triển về mức độ tinh vi, đặc biệt với sự xuất hiện của các mô hình ngôn ngữ lớn (LLM) hỗ trợ tự động hóa quá trình tạo mã độc nhằm tấn công các mục tiêu giá trị cao và rút ngắn thời gian phát triển phần mềm độc hại, các hệ thống phòng thủ truyền thống đang phải đối mặt với nhiều thách thức mới. Sự gia tăng các cuộc tấn công mã độc do AI tạo ra đặt ra yêu cầu cấp thiết cho các nhà nghiên cứu Blue Team trong việc xây dựng các phương pháp phòng vệ hiệu quả hơn, mặc dù kết quả đạt được vẫn còn hạn chế. Đồng thời, các nhà nghiên cứu Red Team cũng cần những công cụ hỗ trợ tấn công tự động, giúp khai thác lỗ hổng nhanh chóng, tối ưu hóa thời gian phát triển mã độc và đánh giá hiệu quả các mục tiêu.   
Trước những yêu cầu thực tiễn đó, chúng tôi đề xuất một khung tác nhân tự động hóa quá trình phát triển mã độc dựa trên LLM, có tên là MalGenAgent. Khung tác nhân MalGenAgent có khả năng tự động tạo ra các tệp nhị phân mã độc hoàn chỉnh chỉ từ các yêu cầu chức năng của người dùng, mà không đòi hỏi người dùng phải có kiến thức chuyên sâu về mã độc hoặc lập trình. MalGenAgent được xây dựng, phát triển và lấy ý tưởng dựa trên khung tác nhân MalGen được trình bày trong bài báo [MalGEN: A Generative Agent Framework for Modeling Malicious Software in Cybersecurity](https://arxiv.org/pdf/2506.07586).
## Kiến trúc MalGenAgent
![image-MalGenAgent](image/1_MalGenAgentImage.png)

Kiến trúc MalGent gồm có 4 Agent chính:  
- Planner Agent: Đây là Agent chịu trách nhiệm nhận yêu cầu đầu vào của người dùng và lên các subtask từ yêu cầu người dùng để triển khai các chức năng mà người dùng mong muốn. Mỗi subtask sẽ là mỗi yêu cầu nhỏ về mã độc của người dùng. Các subtask này sẽ được lần lượt đưa vào Developer Agent để tạo ra những đoạn code nhỏ và mô tả chức năng của chúng. Ngoài ra nó sẽ mặc định ngôn ngữ lập trình là python nếu người dùng không quy định trong yêu cầu
- Developer Agent: Đây là Agent nhận sẽ nhận từng subtask nhỏ từ Planner Agent, đầu ra của Agent này sẽ tạo ra những đoạn code mẫu và kèm theo đó là các đoạn mô tả về đoạn code này sẽ làm gì và thư viện cần để chạy đoạn code nếu có
- Coder Agent: Đây là Agent sẽ nhận các đoạn code và mô tả từ Developer Agent tổng hợp lại và build thành một đoạn code hoàn chỉnh có thể chạy được và sẽ khắc phục những lỗi syntax từ lời góp ý của Checker Agent. Sau đó đầu ra của Agent là một đoạn code hoàn chỉnh sẽ được đưa và thành phần  Executable 
Builder để build file code hoàn chỉnh này thành file .exe cho window hoặc .elf cho linux. Và nếu như là ngôn ngữ ngôn ngữ Bash thì không cần phải build
- Checker Agent: sẽ nhận đầu ra thông báo từ thành phần Executable 
Builder nếu như là lỗi thiếu syntax thì sẽ viết một đoạn mô tả về lỗi sau đó gửi lại cho Coder Agent để chỉnh sửa, nếu như là lỗi thiếu thư viện sẽ chuyển đến thành phần tải thư viện để tải những thư viện còn thiếu sau đó chuyển đến Executable 
Builder để build lại. Nếu như không gặp bất cứ lỗi gì hoàn thành việc tạo malware theo yêu cầu
## Cài đặt
## Hướng dẫn phát triển
## Lưu ý khi sử dụng MalGenAgent
## Lời kết  
