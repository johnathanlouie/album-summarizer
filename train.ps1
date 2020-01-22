conda activate album

foreach ($i in 0..4) { python main.py train vgg2 ccc $i 8 0 2 }
foreach ($i in 0..4) { python main.py train smi ccr $i 14 0 0 }
foreach ($i in 0..4) { python main.py train smi ccr $i 14 7 0 }
foreach ($i in 0..4) { python main.py train smi1 ccrc $i 14 0 0 }
foreach ($i in 0..4) { python main.py train smi lamem $i 14 0 0 }
foreach ($i in 0..4) { python main.py train vgg2 cccaf $i 8 0 2 }
