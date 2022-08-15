import data_handling as dh
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class Vis:
    def __init__(self, test):
        self.test = test

    @staticmethod
    def SetColor(x):
        color_dict = {
            0.60: (45, 15, 65),
            0.68: (61, 20, 90),
            0.7: (78, 26, 111),
            0.705: (94, 31, 136),
            0.71: (116, 39, 151),
            0.715: (151, 52, 143),
            0.72: (184, 66, 140),
            0.725: (219, 80, 135),
            0.73: (233, 106, 141),
            0.735: (239, 139, 150),
            0.740: (242, 172, 162),
            0.742: (249, 204, 171),
            0.745: (255, 226, 174),
            # transition green to red
            # Iquos 29% trigger 0.74 = 280 degrees C
            0.7482: (0, 255, 0),
            # 0.745: (59,252,4), #288 degrees
            0.75: (213, 232, 4),
            0.76: (252, 128, 4),
            0.77: (252, 47, 4),
            # red to white
            0.78: (255, 0, 0),
            0.79: (255, 75, 0),
            0.80: (255, 112, 0),
            0.81: (255, 144, 0),
            0.82: (255, 173, 0),
            0.83: (255, 202, 0),
            0.84: (255, 229, 0),
            0.85: (255, 255, 0),
            0.86: (255, 255, 75),
            0.87: (255, 255, 112),
            0.88: (255, 255, 144),
            0.89: (255, 255, 173),
            0.90: (255, 255, 202),
        }

        color = None
        bin_size = None
        color_dict_keys = list(color_dict.keys())
        color_dict_vals = list(color_dict.values())
        # find the bin that x is in, set colour to corresponding value
        for index, key in enumerate(color_dict):
            if index + 2 == len(color_dict):
                bin_size = color_dict_keys[index + 1] - key
            else:
                bin_size = 1

            if x >= key and x <= key + bin_size:
                color = color_dict[key]
        # check if colour is set, if x is outside bin values set to nearest colour.
        if color is None:
            # set to lower bound
            if x <= color_dict_keys[0]:
                color = color_dict_vals[0]
            # set to higher bound
            elif x >= color_dict_keys[-1]:
                color = color_dict_vals[-1]

        # packs it up into correct string format 'rgb(X, X, X)'
        return "rgb({}, {}, {})".format(color[0], color[1], color[2])

    def plot_classified_test(self, df=None, results=None, echo=True, save=True):
        if df is None:
            df = self.test.sigma_data
        if results is None:
            results = self.test.sigma_results

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # df = df[::5]

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["dRdt"],
                mode="markers",
                marker=dict(
                    size=7, color=list(map(self.SetColor, df["Resistance"].to_list()))
                ),
                name="dRdt",
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df["SMA Thresh"], name="SMA"), secondary_y=False
        )

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["T1 Threshold"],
                name="T1 Threshold",
                fill="tonexty",
                fillcolor="rgba(200,100,200,0.5)",
            ),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["T2 Threshold"],
                name="T2 Threshold",
                fill="tonexty",
                fillcolor="rgba(200,200,100,0.5)",
            ),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(x=df.index, y=df["Resistance"], name="Resistance"),
            secondary_y=True,
        )
        if results["Sigma Detected"]:
            fig.add_annotation(
                x=results["Sigma Puff"],
                y=results["Sigma Resistance"],
                text="Sigma at {}".format(results["Sigma Puff"]),
                showarrow=True,
                arrowhead=1,
                yref="y2",
            )


        if results["IQOS Detected"]:
            fig.add_annotation(
                x=results["IQOS Puff"],
                y=df.loc[results["IQOS Puff"], "Resistance"],
                text="IQOS at {}".format(results["IQOS Puff"]),
                showarrow=True,
                arrowhead=1,
                yref="y2",
            )

        fig.add_annotation(
            text="T1: {}<br>T2: {}<br>SMA Size: {}<br>Std. Dev. Size: {}<br>IQOS Limit: {}<br>IQOS Max. Res: {}<br>Sigma Max. Res: {}".format(results["T1"],
                                                                                                    results["T2"], 
                                                                                                    results["SMA"], 
                                                                                                    results["SD"],
                                                                                                    results["IQOS Limit"],
                                                                                                    results["IQOS Resistance"],
                                                                                                    results["Sigma Resistance"]),
            align="left",
            showarrow=False,
            xref="paper",
            yref="paper",
            x=0.01,
            y=0.8,
            bordercolor="black",
            borderwidth=1,
        )

        fig.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))

        fig.update_layout(
            xaxis_title="Puff Count",
            yaxis_title=r"$\frac{dR}{dt}\text{ [Ω/s]}$",
            title=self.test.test_name,
        )

        fig.add_trace(go.Scatter(x=[results["Sigma Puff"], 1_000_000], y=[results["Sigma Resistance"], results["Sigma Resistance"]], mode='lines', line={'dash': 'dash'}, showlegend=False), secondary_y=True)
        fig.add_trace(go.Scatter(x=[results["Sigma Puff"], results["Sigma Puff"]], y=[results["Sigma Resistance"], -1_000_000], mode='lines', line={'dash': 'dash'}, showlegend=False), secondary_y=True)


        fig.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))

        fig.update_xaxes(range=[-5, 1.1*max(list(df.index)), ])
        fig.update_yaxes(range=[1, 10], secondary_y=False)
        fig.update_yaxes(title_text="Resistance [Ω]", showgrid=False, range=[0.4, 1.5], secondary_y=True)
        fig.update_layout(
            width=1900,
            height=900,
            template="seaborn",
            margin=dict(l=40, r=0, t=40, b=40)
        )
        if echo:
            fig.show()
        if save:
            fig.write_image("Figures/ClassifiedTests/{}.pdf".format(self.test.test_name))
            fig.write_image("Figures/ClassifiedTests/{}.png".format(self.test.test_name), scale=3)

    
