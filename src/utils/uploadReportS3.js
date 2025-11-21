import { 
    S3Client,
    PutObjectCommand,
    CreateBucketCommand,
    DeleteObjectCommand,
    DeleteBucketCommand,
    paginateListObjectsV2,
    GetObjectCommand
} from "@aws-sdk/client-s3";
import dotenv from 'dotenv';
dotenv.config();

export  async function get_s3_file (task_id,bucket_id){

    // this function gets the content of a specific file inside the task_id and a specific bucket
const s3Client =new S3Client({
    region:process.env.REGION_ID,
    credentials:
    {
    accessKeyId:process.env.ACCESS_KEY,
    secretAccessKey:process.env.SECRET_KEY
    }
})

const {Body}=await s3Client.send(
    new GetObjectCommand({
        Bucket:bucket_id,
        Key:`${task_id}.pdf`
    })
)

return await Body.transformToString()
}

export async function iterate_pages(bucket_id){
// this function gets all the pages for a specific bucket
const s3Client =new S3Client({
    region:process.env.REGION_ID,
    credentials:
    {
    accessKeyId:process.env.ACCESS_KEY,
    secretAccessKey:process.env.SECRET_KEY
    }
})

const paginator= paginateListObjectsV2(
    {
        client:s3Client
    },
    {
        Bucket:bucket_id
    }
);

for await (const page of paginator){
    const objects = page.Contents;
    if (objects){
        for (const object of objects){
            console.log(object.Key)
            await s3Client.send(
                new GetObjectCommand({
                    Bucket:bucket_id,
                    Key:object.Key
                })
            )
        }
    }
}

}


const bucket_id= process.env.S3_BUCKET
const task_id="d0d5b083-a60b-4e13-82f0-f9100686215"

const response = await iterate_pages(bucket_id);
