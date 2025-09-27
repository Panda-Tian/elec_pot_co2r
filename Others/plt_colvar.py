#!/usr/bin/env python3
"""
Analyze COLVAR data and generate plots.

This script reads a COLVAR data file, processes the collective variables (CVs),
and generates either 1D or 2D scatter plots depending on the number of CVs provided.
You can optionally color the 1D scatter plot using the OPES.bias data.

Usage:
    plt_colvar.py --filename FILE --cv CV1 [CV2] [CV3] --title TITLE --interval N [--color]

Arguments:
    --filename FILE   The name of the file to read data from (default: "colvar").
    --cv CV1 CV2 CV3   The collective variables to analyze. Provide one CV for a 1D plot,
                      two CVs for a 2D plot, and optionally a third CV for coloring the 2D plot.
                      The default CV is ["c2.max"].
    --title TITLE     The title of the plot (default: "OPES").
    --interval N      The interval of the data to plot (default: 1).
    --color           Use this flag to color the 1D scatter plot with OPES.bias.

Example:
    python plt_colvar.py --filename colvar --cv c4.max --title "xxx"     # 1D plot, without coloring the scatter
    python plt_colvar.py --filename colvar --cv c2.max --title "xxx"  --color  # 1D plot, coloring the scatter with opes.bias
    python plt_colvar.py --filename colvar --cv c1.max c2.max --title xxx
    python plt_colvar.py --filename colvar --cv c1.max c2.max opes1.bias   # coloring the 2D plot with the third CV parameter
    python plt_colvar.py colvar --cv c1.max c2.max --combine    # combine all the colvar files before analysis.
    plt_colvar.py --filename colvar_cb --filter --fcv c1.max d0   # filter the colvar data
Date:
    2024--07--25
"""


import matplotlib.pyplot as plt
import plumed
import argparse
import os, re, sys

parser = argparse.ArgumentParser(description="Analyze PLUMED data.")
parser.add_argument("--filename", type=str, default="colvar", help="The name of the file to read data from.")
parser.add_argument("--combine", action='store_true', help="Combine multiple args.filename (default: colvar) files in the directory before analysis.")
parser.add_argument("--cv", type=str, default=["c2.max"], nargs='+', help="The collective variable to analyze.")
parser.add_argument("--title", type=str, default=None, help="The title of the picture.")
parser.add_argument("--interval", type=int, default=1, help="The interval of the data to plot.")
parser.add_argument("--color", action='store_true', help="Use color for 1D scatter plot.")
parser.add_argument("--no_color", action='store_true', help="Don't use colorbar for 2D scatter plot.")
parser.add_argument("--ax_equal", action='store_true', help="enable x and y axis equal.")
parser.add_argument('--cut_rows', type=int, default=None, help='it set, then read the intial cut_rows data')
parser.add_argument("--save_cv", action='store_true', help="save cvs to a file.")
parser.add_argument("--filter", action='store_true', help="whether to filter the data when upper/lower wall works.")
parser.add_argument("--fcv", type=str, default=['c1.max'], nargs='+', help="assign the cvs for filtering")

args = parser.parse_args()

if args.combine:
    files = os.listdir('.')
    pattern = r'bck\.\d+\.' + re.escape(args.filename)
    colvar_files = sorted(    [f for f in files if re.match(pattern, f)],
                    key=lambda f: int(re.search(r'\d+', f).group())  # sort with the number sequence
                    )
    if args.filename in files:
        colvar_files.append('colvar')
    args.filename = 'COLVAR'   # final output file name
    with open(args.filename, 'w') as outfile:
            for fname in colvar_files:
                with open(fname) as infile:
                    outfile.write(infile.read())

def read_data(filename, num_rows):
    data = plumed.read_as_pandas(filename)
    if num_rows is not None:
        return data.head(num_rows)
    else:
        return data

def plot_cv1D(time, cv1, color, title, ylabel, use_color):
    if use_color:
        sc = plt.scatter(time, cv1, c=color, s=2, cmap='viridis', alpha=0.75)
        cb = plt.colorbar(sc, label='OPES.bias')
        cb.ax.tick_params(labelsize=16)
        cb.ax.yaxis.label.set_size(16)
    else:
        plt.scatter(time, cv1, s=2)

    plt.tick_params(axis='both', labelsize=16)
    font_properties = {'fontsize': 16}
    label_mapping = {'c1.max': 'C.N.(Agtop, C)', 'c2.max': 'C.N.(H, O$_{cd}$)', 'c4.min': 'C.N.(H, O$_{all}$)'}
    ylabel = label_mapping.get(ylabel, ylabel)
    plt.xlabel('Time (ps)', fontdict=font_properties, labelpad=10)
    plt.ylabel(ylabel, fontdict=font_properties, labelpad=10)
    if title !=None:
        plt.title(title, fontdict=font_properties, pad=15)
    plt.show()

def plot_cv2D(cv1, cv2, color, title, xlabel, ylabel, colorlabel, no_color, ax_equal):
    if no_color:
        sc = plt.scatter(cv1, cv2, s=2, alpha=0.75)
    else:
        sc = plt.scatter(cv1, cv2, c=color, s=2, cmap='viridis', alpha=0.75)
        cb = plt.colorbar(sc, label = colorlabel)
        cb.ax.tick_params(labelsize=16)
        cb.ax.yaxis.label.set_size(16)
    # plt.axvline(x=3100, color='r', linestcv1le='--')
    plt.tick_params(axis='both', labelsize=16)
    font_properties = {'fontsize': 16}
    label_mapping = {'c1.max': 'C.N.(Agtop, C)', 'c2.max': 'C.N.(H, O$_{cd}$)', 'c4.min': 'C.N.(H, O$_{all}$)'}
    xlabel = label_mapping.get(xlabel, xlabel)
    ylabel = label_mapping.get(ylabel, ylabel)
    # plt.ylim(0,0.5)
    plt.xlabel(xlabel, fontdict=font_properties, labelpad=10)
    plt.ylabel(ylabel, fontdict=font_properties, labelpad=10)
    if ax_equal:
        plt.axis('equal')
    if title !=None:
        plt.title(title, fontdict=font_properties, pad=15)
    plt.show()

## load COLVAR data
interval=args.interval
data = read_data(args.filename, args.cut_rows)

time= data['time']/1000   # unit: ps

### check whether to filter the data, only for filtering data, doesn't work for plotting

filt_param = {
    'c1.max': {'value': 0.55, 'compare': 'greater'},
    'd0': {'value': 10, 'compare': 'less'},
    'doh_f': {'value': 15, 'compare': 'less'},
    'dOH_wall': {'value': 1.3, 'compare': 'less'},
    'dCO': {'value': 9, 'compare': 'less'},
    'exc_rgn': {'value': 0.01, 'compare': 'less'},
    'logd0': {'value': 0.01, 'compare': 'less'}
}

if args.filter:
    filtered_df = data.copy()  # Start with a copy of the original DataFrame
    for key in args.fcv:
        if key in filt_param:
            param = filt_param[key]
            value = param['value']
            compare = param['compare']
            if compare == 'greater':
                filtered_df = filtered_df[filtered_df[key] > value]
            elif compare == 'less':
                filtered_df = filtered_df[filtered_df[key] < value]
            else:
                print(f'compare type for {key} not recognized')
                sys.exit()
        else:
            print(f'{key} not found in filter parameters')
            sys.exit()

    # Printing the applied filters for clarity
    filter_descriptions = []
    for key in args.fcv:
        if key in filt_param:
            param = filt_param[key]
            compare = param['compare']
            value = param['value']
            if compare == 'greater':
                filter_descriptions.append(f'({key} > {value})')
            elif compare == 'less':
                filter_descriptions.append(f'({key} < {value})')

    print('The colvar data is filtered via ' + ' and '.join(filter_descriptions))
    ## save the filtered data
    filtered_df.to_csv('colvar_fltr', index=False, sep=' ')
    with open('colvar_fltr', 'r') as file:
        lines = file.readlines()
    lines[0] = '#! FIELDS ' + lines[0]
    with open('colvar_fltr', 'w') as file:
        file.writelines(lines)
    print('colvar_fltr file is saved!')
    sys.exit()


## plot the COLVAR data
if len(args.cv) == 1:
    cv1 = data[args.cv[0]]
    color = data['opes1.bias'] if args.color else None
    plot_cv1D(time[::interval], cv1[::interval], color[::interval] if args.color else None, args.title, args.cv[0], args.color)
    output_name = f'{args.cv[0]}.png'
    plt.savefig(output_name, dpi=300, bbox_inches='tight')

elif len(args.cv) >= 2:
    cv1 = data[args.cv[0]]
    if args.cv[1] == 'opes1.bias':
        cv2 = -data[args.cv[1]]
        # args.cv[1]=f'-{args.cv[1]}'
    else:
        cv2 = data[args.cv[1]]

    if len(args.cv)==3:
        color = data[args.cv[2]]  # use the third CV to color the 2D plot
    else:
        color = time # use time to color the 2D plot
    plot_cv2D(cv1[::interval], cv2[::interval], color[::interval], args.title, args.cv[0], f'-{args.cv[1]}' if args.cv[1] == 'opes1.bias' else args.cv[1], args.cv[2] if len(args.cv) == 3 else 'Time (ps)', args.no_color, args.ax_equal)
    output_name = f'2d_{args.cv[0]}-{args.cv[1]}.png'
    plt.savefig(output_name, dpi=300, bbox_inches = 'tight')


if args.save_cv:
    args.cv.insert(0, 'time')
    selected_data = data[args.cv]
    output_filename = 'output.csv'
    selected_data.to_csv(output_filename, index=False)
    print(f"cvs have been saved to {output_filename}")
