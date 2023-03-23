import os
import sys 
import argparse

ADCP_ROOT = '/data/sdd/haotian/alphafold2/autodock/ADFR/bin'
MODPEP_ROOT = '/data/sdd/haotian/alphafold2/modpep/MODPEP_v2.0'
receptor_3q0h = '/data/sdd/haotian/alphafold2/mydata/3q0h-H.pdbqt'


def prepare(args):
    if args.seq is not None:
        if os.path.exists(args.seq):
            print('seq is already existed')
            exit(0)
        dirname = args.seq
    elif args.pdb is not None:
        prefix = args.pdb.split('.')[0]
        if os.path.exists(prefix):
            print('pdb is already existed')
            exit(0)
        dirname = prefix
    os.makedirs(dirname)
    with open(f'{dirname}/peptied.fasta', 'w') as out:
        out.write('> peptide\n')
        out.write(args.seq)
    return dirname

def modpep(args):
    if args.cyc:
        if args.ss:
            s1 = args.ss.split('-')[0]
            s2 = args.ss.split('-')[1]
            os.system(f'{MODPEP_ROOT}/modpep2.0 {args.seq}/peptide.fasta {args.seq}/peptide.pdb -n 100 -L {MODPEP_ROOT} -ss {s1} {s2}')
        else:
            print('disulfide bond not specified')
            exit(0)
    else:
        os.system(f'{MODPEP_ROOT}/modpep2.0 {args.seq}/peptide.fasta {args.seq}/peptide.pdb -n 100 -L {MODPEP_ROOT}')
        

def generate_target(args, dirname):
    # convert to pdb qt
    if not args.target:
        # os.system(f'{ADCP_ROOT}/reduce {dirname}/peptide.pdb > {dirname}/peptide-H.pdb')
        # os.system(f'{ADCP_ROOT}/prepare_ligand -l {dirname}/peptide-H.pdb')
        # # to target 
        # os.system(f'{ADCP_ROOT}/agfr -r {receptor_3q0h} -l {dirname}/peptide-H.pdbqt -o {args.seq}/peptide')
        # return f'{args.seq}/peptide.trg'
        exit('no target file')
    else:
        return args.target


def docking(args, target, dirname):
    os.system(f'cp {target} {dirname}')
    target = target.split('/')[-1]
    os.chdir(dirname)
    if args.cyc: 
        if args.seq and not args.pdb:
            os.system(f'{ADCP_ROOT}/adcp -t {target} -s {args.seq} -N {args.rep} -n {args.iter} -cys -o docking -nc 0.8')
        if not args.seq and args.pdb:
            os.system(f'{ADCP_ROOT}/adcp -t {target} -i {args.pdb} -N {args.rep} -n {args.iter} -cys -o docking -nc 0.8')
    else:
        os.system(f'{ADCP_ROOT}/adcp -t {target} -s {args.seq} -N {args.rep} -n {args.iter} -o docking -nc 0.8')
    os.chdir('..')

def main(args):
    dirname = prepare(args)
    # if args.seq and not args.pdb:
    #     modpep(args)
    #     print('folding peptide')
    target_file = generate_target(args, dirname)
    docking(args, target_file, dirname)
        



if __name__ == "__main__":
    parser = argparse.ArgumentParser('autodock pipeline')
    parser.add_argument('--seq', help='peptide sequence')
    parser.add_argument('--ss', help='disulfide bond, seperated by "-" ')
    parser.add_argument('--pdb', help='pdb file of conformations')
    parser.add_argument('--target', help='ADCP target file of a known ligand binding with the receptor')
    parser.add_argument('--rep', help='number of replica for ADCP', type=int, default=100)
    parser.add_argument('--iter', help='number of iteration for ADCP', type=int, default=1000000)
    parser.add_argument('--cyc', help='if cyclic is allowed', action='store_true')
    args = parser.parse_args()
    main(args)




