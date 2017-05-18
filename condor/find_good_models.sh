grep -B 1 "multFac" mlp_2863_manyClf.out | awk -F'-' '{print $9}' > accuracies_manyClf.txt
grep "acc" accuracies_manyClf.txt > accuracies_manyClf_2.txt
mv accuracies_manyClf_2.txt accuracies_manyClf.txt
cat -n accuracies_manyClf.txt > accuracies_manyClf_n.txt
awk '$3 > 0.80 {print $1}' accuracies_manyClf_n.txt > good_ind.txt
echo "Number of good predictions"
wc -l good_ind.txt
tr '\n' ',' < good_ind.txt > good_ind_parsed.txt

