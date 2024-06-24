A messaging system backend in the cloud!

This project develops a backend for a cloud-based messaging system akin to Telegram or WhatsApp. 
The backend is designed to handle user registrations, one-on-one and group messaging (including managing groups: adding, removing), user blocking,supporting scaling from thousands to millions of users.

Technologies Used
Redis: Utilized for fast data caching and managing user sessions to enhance performance and response times.
MongoDB: Serves as the primary database for persisting user details, messages, and group information, chosen for its scalability and flexibility in handling large datasets.
Sharding: Implemented using receiver_id to distribute data across multiple database instances, optimizing load balancing and improving data retrieval speeds. 
The decision to avoid using sender_id for sharding is influenced by the requirement to support group messaging effectively.

Features:
User Registration: Allows new users to sign up by generating a unique ID.
Message Sending: Supports sending messages directly to other users and checks if the sender is blocked.
Block Management: Users can block or unblock others to prevent or allow incoming messages.
Group Functions: Includes creating groups, adding or removing users, and managing group messages.
Scaling Strategy
Redis: Reduces the load on the main database by caching frequently accessed data, significantly improving the system's responsiveness and ability to handle simultaneous requests.
Sharding: By sharding the database with the receiver_id, we ensure even distribution of data, which is crucial for maintaining performance as the user base grows.
MongoDB: Known for its robust handling of large volumes of data, MongoDB facilitates easy horizontal scaling, which is critical when expanding to accommodate more users.



This backend system is built with scalability and efficiency in mind, utilizing Redis for caching, MongoDB for persistence, and sharding techniques to handle growth effectively, making it robust for deployment in cloud environments.
