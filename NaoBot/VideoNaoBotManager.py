# coding : utf-8

'''
Copyright 2020 Agnese Salutari.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License
'''


from naoqi import ALProxy
import vision_definitions
import time
from PIL import Image
import base64
import cStringIO

from RedisManager import RedisManager
from TimeManager import getTimestamp
from Configs import RedisConfig, NaoConfig


def saveImageOnRedis(redis, base64Capture):
    timestamp = getTimestamp()
    redis.hsetOnRedis(key=RedisConfig['imageHsetRoot']+str(timestamp), field=RedisConfig['imageHsetB64Field'],
                      value=base64Capture)
    redis.publishOnRedis(channel=RedisConfig['newImagePubSubChannel'],
                         msg=RedisConfig['newImageMsgRoot']+str(timestamp))

def main():
    resolution = vision_definitions.kQVGA
    colorSpace = vision_definitions.kYUVColorSpace
    camProxy = ALProxy("ALVideoDevice", NaoConfig['IP'], NaoConfig['PORT'])
    camSub = camProxy.subscribe("python_client", resolution, colorSpace, NaoConfig['imageFPS'])
    r = RedisManager(host=RedisConfig['host'], port=RedisConfig['port'], db=RedisConfig['db'],
                     password=RedisConfig['password'], decodedResponses=RedisConfig['decodedResponses'])
    while True:
        naoImage = camProxy.getImageRemote(camSub)
        im = Image.fromstring("RGB", (naoImage[0], naoImage[1]), naoImage[6])
        buffer = cStringIO.StringIO()
        im.save(buffer, format="JPEG")
        imgB64 = base64.b64encode(buffer.getvalue())
        saveImageOnRedis(r, imgB64)
        time.sleep(NaoConfig['videoSleepSec'])


if __name__ == '__main__':
    main()