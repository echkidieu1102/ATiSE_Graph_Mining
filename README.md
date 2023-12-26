## Course: Graph Mining

Graph Data Mining Course Project, Exploring the  Additive Time Series Decomposition (ATiSE) Model.

### Mô tả dữ liệu: YAGO11k, Wikidata12k, ICEWS14, ICEWS05-15 lần lượt đều là những bộ dữ liệu tập con của những tập dữ liệu YAGO3, Wikidata, ICEWS.

- **YAGO:** Được lưu theo chuẩn RDF (Resource Description Framework) - là phương pháp chung để mô tả và trao đổi dữ liệu dạng đồ thị Subject-Relation-Object
    - Nguồn: là tập con của YAGO được tạo ra từ Wikipedia, WordNet, WikiData, GeoNames và các nguồn dữ liệu khác.
    - Độ chính xác của YAGO đã được kiểm tra thủ công, chứng minh một độ chính xác xác nhận là [95%](https://www.mpi-inf.mpg.de/departments/databases-and-information-systems/research/yago-naga/yago)
    - Ví dụ:
        - (`Elvis`, `birthPlace`, `Tupelo`, `1935-01-08`, `1977-08-16`)
        - (`Paul Konchesky`, `playsFor`, `England national football team`, `2003-##-##`, `2005-##-##`)
- **Wikidata:**
    - Nguồn: các dự án Wikimedia khác, cộng đồng người dùng từ khắp nơi trên thế giới. Tập dữ liệu được cập nhật liên tục với các đóng góp mới từ người dùng hoặc tự động dựa trên các nguồn tin tức, thời sự, trang web chính phủ,...
    - Wikidata là một cơ sở tri thức miễn phí và mở có thể được đọc và chỉnh sửa bởi cả con người và máy móc.
    - Ví dụ:
        - (`509`, `1`,`442`,`1713-##-##`,`1783-##-##`)
        - (`8847`,`17`,`8848`,`2003-##-##`,`2003-##-##`)
- **ICEWS**
    - Nguồn: được thu thập từ nhiều nguồn khác nhau, bao gồm các bài báo tin tức, các trang web chính phủ và các nguồn tin tức xã hội.
    - ICEWS là một kho chứa các sự kiện chính trị với một dấu thời gian cụ thể.
    - Tập dữ liệu ICEWS05-15 mô tả các sự kiện chính trị xảy ra từ 2005 đến 2015, ICEWS14 mô tả các sự kiện chính trị xảy ra vào năm 2014
    - Ví dụ:
        - (`Laos`,`Host a visit`,`Nguyen Xuan Phuc`,`2014-12-12`)
        - (`Ministry (Vietnam)`,`Make statement`,`Vietnam`,`2013-08-27`)
