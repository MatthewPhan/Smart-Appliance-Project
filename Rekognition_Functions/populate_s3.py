import boto3

s3 = boto3.resource('s3')

# Get list of objects for indexing
images=[('image01.jpeg','Matthew'),
      ('image02.jpeg','Matthew'),
      ('image03.jpeg','James'),
      ('image04.jpeg','James'),
      ]

# Iterate through list to upload objects to S3   
for image in images:
    file = open(image[0],'rb')
    object = s3.Object('smart-appliance-bucket','index/'+ image[0])
    ret = object.put(Body=file,
                    Metadata={'FullName':image[1]}
                    )