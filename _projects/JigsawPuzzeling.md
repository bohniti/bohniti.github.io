---
layout: project
title: Solving a Jigsaw Puzzle
subtitle: Use deep learning to automatically solve a puzzle.
subsubtitle: February 2019
image: jigsaw.png

---

## Intro

The scope of the project is the association of historical fragments using deep metric learning. More precisely, I'm
interested in the fragments from the HisFrac20 Dataset, and the objective is to reconstruct them before their analysis
by archeology experts. The task is challenging since image size is large, the images are from a broad domain, and
it is also hard for humans to notice the minor differences which distinguish two fragments.

## Dataset

The dataset contains a set of pages from different writers split into fragments.
As can be seen most of the pages are split into 1 to 4 fragments. Some are split into many more fragments:
<center>
<div style="margin:0 60px 0px 0">
<img src="../../public/images/Puzzeling/fragments_per_page.png" align=center width=1000>
</div>
</center>
The fragments are shaped quite differently:
<center>
<div style="margin:0 60px 0px 0">
<img src="../../public/images/Puzzeling/random_sample.png" align=center width=1000>
</div>
</center>
As said in the introduction, its not easy to distiung different pages even if they are from a different page:
<center>
<div style="margin:0 60px 0px 0">
<img src="../../public/images/Puzzeling/writer_sample.png" align=center width=1000>
</div>
</center>

## Methods

### Siamese Networks

A Siamese neural network (sometimes called a twin neural network) is an artificial neural network
containing two or more identical subnetwork components that share their weights (hence the name
"Siamese"). This kind of neural network, first introduced by Bromley et al. in 1994 to tackle
automatic signature verification, is specifically designed for tasks involving (dis)similarity.
It is a good match for the task of puzzle-solving since the approach is to determine if an image is a
neighbor from another fragment or not.

### ResNet50

The ResNets (Residual Networks) were introduced by Kaiming He et al. as a novel, very deep architecture that can be efficiently trained using residual learning blocks implementing
shortcut connections to mitigate the issue of vanishing gradients with deep networks. I used an architecture similar to this:

<center>
<div style="margin:0 60px 0px 0">
<img src="../../public/images/Puzzeling/restnet50.png" align=center width=1000>
</div>
</center>

But instead of feeding just one input to the network, both images (example and counterexample) are given as an input with shared weights (see above).

### Results

The main problem was the size of the dataset and the size of the fragments themselves. This leads to high computational cost what made training difficult and slow.
Nevertheless, it could be shown that the network is learning, and with more fine-tuning, the results could go towards 60 percent.


<center>
<div style="margin:0 60px 0px 0">
<img src="../../public/images/Puzzeling/results.png" align=center width=1000>
</div>
</center>
