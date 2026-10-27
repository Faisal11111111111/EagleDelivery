"""Create the three-page report from the saved experiment results."""
import csv
from pathlib import Path
import matplotlib

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                               TableStyle, Image, PageBreak)

ROOT = Path(__file__).resolve().parent


def read_csv(name):
    with (ROOT / "results" / name).open(newline="") as stream:
        return list(csv.DictReader(stream))


def main():
    fonts = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
    for name, filename in (("ReportSans", "DejaVuSans.ttf"),
                           ("ReportSans-Bold", "DejaVuSans-Bold.ttf"),
                           ("ReportSans-Italic", "DejaVuSans-Oblique.ttf"),
                           ("ReportSans-BoldItalic", "DejaVuSans-BoldOblique.ttf")):
        pdfmetrics.registerFont(TTFont(name, str(fonts / filename)))
    pdfmetrics.registerFontFamily("ReportSans", normal="ReportSans", bold="ReportSans-Bold",
                                 italic="ReportSans-Italic", boldItalic="ReportSans-BoldItalic")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="BodyCustom", fontName="ReportSans", fontSize=9.6,
                              leading=12.7, spaceAfter=7))
    styles.add(ParagraphStyle(name="SmallCustom", fontName="ReportSans", fontSize=8.2,
                              leading=10.7, spaceAfter=5))
    styles.add(ParagraphStyle(name="TitleCustom", fontName="ReportSans-Bold", fontSize=19,
                              leading=23, spaceAfter=6))
    styles.add(ParagraphStyle(name="HeadingCustom", fontName="ReportSans-Bold", fontSize=12,
                              leading=15, spaceBefore=6, spaceAfter=7))
    styles.add(ParagraphStyle(name="CellCustom", fontName="ReportSans", fontSize=8.6,
                              leading=11, alignment=TA_CENTER))

    def p(text, style="BodyCustom"):
        return Paragraph(text, styles[style])

    def table(rows, widths):
        data = [[p(str(cell), "CellCustom") for cell in row] for row in rows]
        result = Table(data, colWidths=widths, hAlign="LEFT", repeatRows=1)
        result.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#edf0f2")),
            ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.HexColor("#70787e")),
            ("LINEBELOW", (0, 1), (-1, -1), 0.3, colors.HexColor("#d5dadd")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        return result

    def figure(name, width, height):
        return Image(str(ROOT / "plots" / name), width=width, height=height)

    search = read_csv("search_comparison.csv")
    evaluation = {r["condition"]: r for r in read_csv("evaluation_comparison.csv")}
    windows = {(r["condition"], r["window"]): r for r in read_csv("training_windows.csv")}
    story = []
    story += [p("Eagle Delivery", "TitleCustom"),
              p("Faisal Abusara | COSC 461 | Project 1 | October 26, 2026", "SmallCustom"),
              p("Part A: Planning with BFS and A*", "HeadingCustom")]
    story.append(p("The task is to deliver a package between two building entrances. "
        "The robot plans on a known map, then learns delivery behavior by interacting with the same environment."))
    story.append(p("<b>Problem formulation.</b> A state is the robot's (row, column) position. "
        "The initial state is the selected starting entrance: S, L, or H for the required tasks. "
        "Actions are UP, DOWN, LEFT, and RIGHT. In the deterministic transition model, a valid "
        "action moves one cell; a wall or boundary leaves the robot in place. The goal test checks "
        "whether the position equals the selected destination. Each attempted action costs 1, "
        "so path cost is the number of actions. Search uses valid neighboring cells because "
        "a failed move cannot improve a shortest path."))
    story.append(p("<b>Why BFS is optimal.</b> BFS explores routes in increasing numbers of moves. "
        "Since every move has the same cost, the first goal it removes from its queue has minimum cost."))
    story.append(p("<b>Heuristic and implementation.</b> Manhattan distance is "
        "h(s) = |row(s) - row(goal)| + |column(s) - column(goal)|. With no diagonal moves, "
        "the robot must cover at least these row and column differences. Walls may add steps, "
        "so the heuristic never overestimates the shortest route. A* uses f = g + h, insertion "
        "order for equal-f ties, and the supplied UP, DOWN, LEFT, RIGHT neighbor order. A strictly "
        "cheaper route replaces the stored cost and parent. Stale queue entries are skipped, "
        "and the goal is checked after removing a current entry."))
    story.append(p("Search comparison", "HeadingCustom"))
    rows = [["Map", "Task", "BFS<br/>length", "A*<br/>length", "BFS<br/>expanded", "A*<br/>expanded"]]
    for r in search[:6]:
        rows.append(["Baseline" if r["map"] == "emu_campus" else "Detour", r["task"],
                     r["bfs_length"], r["astar_length"], r["bfs_expanded"], r["astar_expanded"]])
    story.append(table(rows, [100, 65, 78, 78, 95, 95]))
    story.append(Spacer(1, 7))
    story.append(p("Length counts actions, so it is len(path) - 1. A node is expanded only "
        "when its successors are generated; the goal is not counted. Start = goal returns "
        "a one-state path and zero expansions. An unreachable goal returns no path.", "SmallCustom"))
    story.append(p("Both algorithms found equal-length routes in all six cases. A* expanded "
        "fewer nodes in these runs, although that is not guaranteed for every map. For baseline "
        "S-W, expansions fell from 67 to 22. The closure increased the S-W route from 18 to 26 "
        "actions, while L-D and H-P kept the same shortest lengths. These results show that "
        "the heuristic can reduce search work without changing route quality."))
    story.append(p("Validation: all 14 supplied unit tests passed. Full search routes and counts "
        "are saved in results/search_routes.txt and results/search_comparison.csv.", "SmallCustom"))
    story.append(p("Source files: the provided assignment and starter simulator. All measurements "
        "were generated by running this implementation; raw CSVs, per-seed summaries, "
        "commands, the prediction, and plotting code accompany the report.", "SmallCustom"))

    story += [PageBreak(), p("Part B: Learning a delivery policy", "HeadingCustom")]
    story.append(p("<b>Learning rule.</b> The Q-table is a dictionary keyed by (state, action), "
        "with unseen values equal to 0. Epsilon-greedy selection chooses uniformly from all "
        "four actions with probability epsilon; otherwise, it chooses uniformly among the "
        "actions tied for the highest Q-value. Both choices use the supplied random generator. "
        "The update changes only the observed state-action entry:"))
    story.append(p("Q(s,a) &larr; Q(s,a) + alpha [target - Q(s,a)]<br/>"
        "target = reward at the goal; otherwise reward + gamma max Q(next state, next action)."))
    story.append(p("The maximum includes unseen actions with value zero. Goal arrival has no "
        "continuation value. A nonterminal collection cutoff still uses the observed nonterminal "
        "update. The learner uses interaction only; it never calls BFS or A*."))
    story.append(p("<b>Settings.</b> For each baseline task, seeds 0, 1, and 2 each started with "
        "an empty Q-table and trained for 2,000 episodes. Alpha was 0.3, gamma 0.95, constant "
        "epsilon 0.2, and slip 0. Each episode allowed up to 200 attempted actions. After training, "
        "each table was evaluated for 100 episodes with epsilon 0 and learning frozen. This gives "
        "nine training runs and 900 evaluation episodes."))
    rows = [["Task", "Eval.<br/>success", "Eval.<br/>steps", "Eval.<br/>return", "First 100<br/>train success", "Last 100<br/>train steps"]]
    for name in ("baseline_SW", "baseline_LD", "baseline_HP"):
        e = evaluation[name]; first = windows[name, "first100"]; last = windows[name, "last100"]
        rows.append([e["task"], f'{float(e["success_rate"])*100:.0f}%',
                     f'{float(e["mean_steps_success"]):.0f}', f'{float(e["mean_return"]):.0f}',
                     f'{float(first["success_rate"])*100:.1f}%', f'{float(last["mean_steps"]):.2f}'])
    story.append(table(rows, [49, 80, 67, 70, 123, 122]))
    story.append(Spacer(1, 6))
    story.append(p("Values combine the three seeds equally. Evaluation steps count successful "
        "deliveries; training steps include failures. Each seed had the same final evaluation "
        "success, steps, and return, giving sample SD = 0 for those final measures.", "SmallCustom"))
    story.append(figure("baseline_learning.png", 511, 184.53))
    story.append(p("Figure 1. Training means over the three seeds in non-overlapping blocks of "
        "100 episodes. The success axis begins at 75%. Failures remain included in both measures.", "SmallCustom"))
    story.append(p("<b>What the results show.</b> The final learned routes matched BFS's shortest "
        "lengths: 18, 22, and 16 actions. Their returns were 22, 18, and 24, matching 40 minus "
        "delivery length. Training was less efficient because random actions continued with "
        "epsilon 0.2. For example, late S-W training averaged 22.58 actions, compared with 18 "
        "during evaluation. Mean returns improved sharply after the early episodes, but the "
        "three tasks did not have identical early success rates."))
    story.append(p("Training had 51 S-W failures, 26 L-D failures, and 46 H-P failures across "
        "6,000 episodes per task. All were retained. The final 100 training episodes succeeded "
        "for every seed and task. Perfect final evaluation here describes these fixed, "
        "deterministic tasks; it does not establish performance on other maps or with slipping."))

    story += [PageBreak(), p("Part C: Custom map and exploration experiment", "HeadingCustom")]
    story.append(p("<b>Question:</b> How does exploration affect learning and final S-W delivery "
        "performance? <b>Prediction, recorded before the runs:</b> epsilon 0.05 should waste "
        "fewer actions once it learns a route; 0.5 should explore more but take longer during "
        "training. Epsilon 0.2 might offer a balance. All three may eventually learn the same "
        "shortest route when exploration is turned off."))
    map_text = p("<b>Map design.</b> The map is 11 by 17 cells, with a blocked border and all "
        "six building letters exactly once. All entrances are connected. Using zero-based "
        "coordinates, the main loop has corners (3,1), (3,15), (7,15), (7,1). The branch from "
        "(3,7) ends at D = (5,7). Crossing on row 3 gives an 18-action route; going via row 7 "
        "takes 26 actions. BFS and A* both found length 18, with 53 and 32 expansions.", "SmallCustom")
    map_table = Table([[figure("custom_map.png", 222, 143.07), map_text]], colWidths=[234, 277])
    map_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                                   ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                   ("RIGHTPADDING", (0, 0), (-1, -1), 8)]))
    story.append(map_table)
    story.append(p("<b>Controlled procedure.</b> Only constant training epsilon changed: 0.05, "
        "0.2, or 0.5. The map and S-W task stayed fixed. Every setting used fresh tables for "
        "seeds 0, 1, 2 and the same alpha, gamma, slip, episode counts, and action limit as "
        "Part B. Evaluation again froze learning and used epsilon 0."))
    rows = [["Training<br/>epsilon", "First 100<br/>success", "Last 100<br/>steps", "Last 100<br/>return", "Training<br/>failures", "Eval. success<br/>/ steps"]]
    for name in ("custom_e005", "custom_e020", "custom_e050"):
        e = evaluation[name]; first = windows[name, "first100"]; last = windows[name, "last100"]
        total = windows[name, "all"]
        rows.append([f'{float(e["epsilon"]):.2f}', f'{float(first["success_rate"])*100:.1f}%',
                     f'{float(last["mean_steps"]):.2f}', f'{float(last["mean_return"]):.2f}',
                     total["truncated"], f'{float(e["success_rate"])*100:.0f}% / {float(e["mean_steps_success"]):.0f}'])
    story.append(table(rows, [68, 86, 87, 87, 83, 100]))
    story.append(Spacer(1, 5))
    story.append(p("Training windows average 100 episodes per seed (300 total); failures count "
        "all 6,000 training episodes per setting. Evaluation has 300 episodes per setting. "
        "All evaluation returns were 22, with zero between-seed SD.", "SmallCustom"))
    story.append(figure("custom_exploration.png", 511, 184.53))
    story.append(p("Figure 2. Custom-map training means across seeds in 100-episode blocks; "
        "the success axis begins at 75%.", "SmallCustom"))
    story.append(p("<b>Findings.</b> The prediction about training efficiency was supported: "
        "late training averaged 19.00 actions at epsilon 0.05 and 35.35 at 0.5. Higher exploration "
        "kept causing extra actions even after a good route was learned. All three settings "
        "reached the same 18-action route in every evaluation episode. Epsilon 0.2 showed no "
        "final advantage here. The 20, 22, and 28 training failures were all kept in the results. "
        "Three seeds on one map are not enough to conclude that low exploration is always best; "
        "a larger or less familiar map could need more exploration."))

    def page_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("ReportSans", 8)
        canvas.setFillColor(colors.HexColor("#555555"))
        canvas.drawString(50.5, 27, "Eagle Delivery | Faisal Abusara")
        canvas.drawRightString(561.5, 27, str(doc.page))
        canvas.restoreState()

    doc = SimpleDocTemplate(str(ROOT / "EagleDelivery_Report.pdf"), pagesize=(612, 792),
                            rightMargin=50.5, leftMargin=50.5, topMargin=37, bottomMargin=40,
                            title="Eagle Delivery - Project 1", author="Faisal Abusara")
    doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
    print("Created EagleDelivery_Report.pdf")


if __name__ == "__main__":
    main()
