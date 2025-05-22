import io
import base64
import urllib.parse

from cycler import cycler
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

#'tab10', 'Dark2'
cores = plt.get_cmap('Dark2').colors
cores = [plt.matplotlib.colors.to_hex(color) for color in cores]

params = {
    'axes.prop_cycle':cycler('color', cores),
    'axes.titlecolor':'gray',
    'figure.figsize':(4, 2.8),
    'axes.titley':1.05,
    'axes.titlesize' : 10,
    'xtick.labelsize' : 7,
    'ytick.labelsize' : 7,
    'axes.spines.left': False,  # display axis spines
    'axes.spines.bottom': False,
    'axes.spines.top': False,
    'axes.spines.right': False,
}
#https://matplotlib.org/stable/users/explain/customizing.html
#plt.style.use('ggplot')
plt.rcParams.update(params)

def salvar_figura(fig: plt.figure):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=300)
    buf.seek(0)
    string = base64.b64encode(buf.read()).decode('utf-8')
    uri = urllib.parse.quote(string)
    return(uri)

def grafico_linha(array_x: list, array_y: list, titulo:str, grupo:list | None=[], figsize: tuple | None = (4, 2.8)):
    fig = plt.figure(figsize=figsize)
    axs = fig.subplot_mosaic('A')
    n = 0
    for elemento in set(grupo):
        x = array_x[grupo == elemento]
        y = array_y[grupo == elemento]
        axs['A'].plot(x, y, label = elemento, color=cores[n], marker='o', linestyle='dashed', linewidth=2, markersize=12)
        n +=1
    axs['A'].set_title(titulo)
    #axs['A'].set_frame_on(False)
    axs['A'].grid(True, axis='y', linewidth=0.4, linestyle='-')
    axs['A'].tick_params(axis='both', colors='grey')
    axs['A'].legend()
    img = salvar_figura(fig)
    plt.close()
    return(img)

def grafico_barra(array_x: list, array_y: list, titulo:str):
    fig = plt.figure()
    axs = fig.subplot_mosaic('A')
    barra = axs['A'].bar(array_x, array_y)
    axs['A'].bar_label(barra, array_y, color=cores[0], fontweight='semibold')
    axs['A'].set_title(titulo)
    #axs['A'].set_frame_on(False)
    axs['A'].grid(True, axis='y', linewidth=0.4, linestyle='-')
    axs['A'].tick_params(axis='both', colors='grey')
    img = salvar_figura(fig)
    plt.close()
    return(img)

def grafico_pizza(titulo, **arg_pie):
    fig = plt.figure()
    axs = fig.subplot_mosaic('A')
    patches, texts, autotexts = axs['A'].pie(**arg_pie)
    for patch, text in zip(patches, texts):
        text.set_color(patch.get_facecolor())
    axs['A'].set_title(titulo)
    img = salvar_figura(fig)
    plt.close()
    return(img)

def grafico_kpi(valor: int, rotulo: str, exibir_percentual:bool | None=False, cor: str | None=cores[0], exibir_posicao:bool | None = False):
    valor = str(valor)
    if exibir_percentual:
        valor = f'{str(valor)} %'
    if exibir_posicao:
        valor = f'{str(valor)} º'
    fig = plt.figure(figsize=(4, 1.8))
    axs = fig.subplot_mosaic('A')
    axs['A'].text(0.5, 0.6, valor, ha='center', va='center', fontsize=60, color = cor, fontweight='semibold')
    axs['A'].text(0.5, 0.1, rotulo, ha='center', va='center', fontsize=12, color='grey')
    #axs['A'].set_title(titulo, {'color':'grey'})
    axs['A'].axis('off')
    img = salvar_figura(fig)
    plt.close()
    return(img)
