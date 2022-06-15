import tensorflow as tf
import numpy as np
import cv2

from PIL import Image

print(tf.__version__)

model = tf.saved_model.load('./saved_model/')
results = [
    ("primrose", 3),
    ("orchid", 3),
    ("campanular", 2),
    ("sweet pea", 3),
    ("marigold", 3),
    ("tiger lily", 3),
    ("phalaenopsis", 2),
    ("strelitzia", 2),
    ("aconitum", 2),
    None,
    ("snapdragon", 3),
    None,
    None,
    ("cirsium", 3),
    ("iris", 3),
    None,
    ("coneflower", 3),
    ("lily", 3),
    ("platycodon", 2),
    ("lily", 3),
    ("clivia", 2),
    ("scabiosa", 2),
    None,
    None,
    ("grape hyacinth", 3),
    ("poppy", 3),
    None,
    ("gentian", 3),
    None,
    ("dianthus", 2),
    ("carnation", 3),
    ("phlox", 3),
    None,
    ("aster", 3),
    None,
    ("cattleya", 3),
    None,
    None,
    None,
    ("helleborus", 3),
    ("barberton daisy", 3),
    ("daffodil", 3),
    ("sword lily", 3),
    ("poinsettia", 3),
    None,
    None,
    ("marigold", 3),
    ("buttercup", 3),
    None,
    ("dandelion", 3),
    ("petunia", 3),
    ("pansy", 3),
    ("primula", 2),
    ("sunflower", 3),
    ("pelargonium", 2),
    None,
    None,
    ("pelargonium", 2),
    ("dahlia", 3),
    ("dahlia", 3),
    None,
    ("anemone", 2),
    None,
    None,
    ("poppy", 3),
    None,
    ("crocus", 3),
    ("iris", 3),
    ("windflower", 3),
    ("poppy", 3),
    None,
    ("azalea", 3),
    ("waterlily", 3),
    ("rose", 3),
    None,
    ("morning glory", 3),
    None,
    ("lotus", 3),
    ("toad lily", 3),
    ("anthurium", 2),
    None,
    ("clematis", 2),
    ("hibiscus", 2),
    None,
    ("desert rose", 3),
    ("tree mallow", 3),
    ("magnolia", 3),
    ("cyclamen", 2),
    None,
    ("canna", 2),
    None,
    None,
    None,
    ("digitalis", 2),
    ("bougainvillea", 2),
    ("camellia", 2),
    ("mallow", 3),
    ("petunia", 3),
    None,
    None,
    ("creeper", 3),
    None
]

def classify_image(image):
    res = model(image)
    print(res)

    idx = np.argmax(res)

    return results[idx]

if __name__ == '__main__':
    with open('test2.jpg', 'rb') as f:
        img = cv2.imdecode(np.asarray(bytearray(f.read())), cv2.IMREAD_COLOR)
    
    cv2.imshow('', img)
    cv2.waitKey(0)

    img = cv2.resize(img, dsize=(224, 224))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.reshape(1, 224, 224, 3).astype(np.float32) / 255

    print(classify_image(img))