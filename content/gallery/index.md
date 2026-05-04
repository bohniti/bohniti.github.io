+++
title = "Gallery"
type = "gallery"

[build]
publishResources = false

# === Photo Resources ===
# 18 [[resources]] entries, one per photo in content/gallery/photos/.
# - src/name byte-match filename casing (Pitfall 14 — DO NOT normalize).
# - alt is REQUIRED (D-03; lightbox image is primary content of <dialog>).
# - weight is REQUIRED, unique integer (D-04; deterministic order, increments of 10 leave room for inserts).
# - caption is OPTIONAL (D-02; omit the line entirely when not authored — `with $photo.Params.caption` template guard handles graceful empty rendering).

[[resources]]
src = "photos/IMG_8113.jpg"
name = "photos/IMG_8113.jpg"
[resources.params]
alt = "A landscape photograph from Timo's travels."
weight = 10

[[resources]]
src = "photos/IMG_7828.jpeg"
name = "photos/IMG_7828.jpeg"
[resources.params]
alt = "A scenic photograph captured during a walk."
weight = 20

[[resources]]
src = "photos/IMG_6546.jpeg"
name = "photos/IMG_6546.jpeg"
[resources.params]
alt = "An outdoor photograph from a recent trip."
weight = 30

[[resources]]
src = "photos/IMG_5685_Original.JPG"
name = "photos/IMG_5685_Original.JPG"
[resources.params]
alt = "A candid photograph from the field."
weight = 40

[[resources]]
src = "photos/IMG_2009.jpeg"
name = "photos/IMG_2009.jpeg"
[resources.params]
alt = "A photograph documenting a moment outdoors."
weight = 50

[[resources]]
src = "photos/IMG_1646.jpeg"
name = "photos/IMG_1646.jpeg"
[resources.params]
alt = "A landscape view from a hike."
weight = 60

[[resources]]
src = "photos/IMG_1499.jpeg"
name = "photos/IMG_1499.jpeg"
[resources.params]
alt = "A photograph from an outdoor adventure."
weight = 70

[[resources]]
src = "photos/IMG_1299.JPG"
name = "photos/IMG_1299.JPG"
[resources.params]
alt = "A photograph documenting an outdoor moment."
weight = 80

[[resources]]
src = "photos/IMG_1288.JPG"
name = "photos/IMG_1288.JPG"
[resources.params]
alt = "A photograph from the road."
weight = 90

[[resources]]
src = "photos/IMG_0256.jpeg"
name = "photos/IMG_0256.jpeg"
[resources.params]
alt = "A photograph captured during travel."
weight = 100

[[resources]]
src = "photos/DSC09784.JPG"
name = "photos/DSC09784.JPG"
[resources.params]
alt = "A photograph from a camera shoot outdoors."
weight = 110

[[resources]]
src = "photos/DSC09782.JPG"
name = "photos/DSC09782.JPG"
[resources.params]
alt = "A photograph from a camera shoot outdoors."
weight = 120

[[resources]]
src = "photos/20210710_132418.jpg"
name = "photos/20210710_132418.jpg"
[resources.params]
alt = "A photograph from July 2021."
weight = 130

[[resources]]
src = "photos/5dc795b8-3921-45b8-a651-5b434e405259.jpg"
name = "photos/5dc795b8-3921-45b8-a651-5b434e405259.jpg"
[resources.params]
alt = "A photograph documenting a personal moment."
weight = 140

[[resources]]
src = "photos/60130366-e95c-48a9-b8cd-aa38090c02c2.jpg"
name = "photos/60130366-e95c-48a9-b8cd-aa38090c02c2.jpg"
[resources.params]
alt = "A photograph from an outdoor activity."
weight = 150

[[resources]]
src = "photos/7eb72991-8aac-44e7-92f7-f71968357ceb.jpg"
name = "photos/7eb72991-8aac-44e7-92f7-f71968357ceb.jpg"
[resources.params]
alt = "A photograph captured outdoors."
weight = 160

[[resources]]
src = "photos/98562fcd-4559-4d91-8020-48ac5dbc9610.jpg"
name = "photos/98562fcd-4559-4d91-8020-48ac5dbc9610.jpg"
[resources.params]
alt = "A photograph from a personal outing."
weight = 170

[[resources]]
src = "photos/f2e6acbb-7e38-4235-aade-b23a22622596.jpg"
name = "photos/f2e6acbb-7e38-4235-aade-b23a22622596.jpg"
[resources.params]
alt = "A photograph from a memorable trip."
weight = 180
+++
