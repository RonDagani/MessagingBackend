from scripts import uploadDockerImage, uploadServerless, uploadPersistance
import pulumi

repo, image = uploadDockerImage.upload()
redis_host, redis_port, mongodb_connection_string_modified = uploadPersistance.upload()

env_vars = pulumi.Output.all(redis_host, redis_port, mongodb_connection_string_modified).apply(
    lambda values: {
        "REDIS_HOST": values[0],
        "REDIS_PORT": values[1],
        "MONGODB_CONNECTION_STRING": values[2],
    }
)

print(env_vars)

uploadServerless.upload(repo, image, env_vars)