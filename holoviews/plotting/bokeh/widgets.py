import json
from distutils.version import LooseVersion

import param
import bokeh
from bokeh.io import push_notebook, Document

if LooseVersion(bokeh.__version__) >= LooseVersion('0.11'):
    old_bokeh = False
    from bokeh.io import _CommsHandle
    from bokeh.util.notebook import get_comms
else:
    old_bokeh = True

from ..widgets import NdWidget, SelectionWidget, ScrubberWidget


class BokehWidget(NdWidget):

    css = param.String(default='bokehwidgets.css', doc="""
        Defines the local CSS file to be loaded for this widget.""")

    extensionjs = param.String(default='bokehwidgets.js', doc="""
        Optional javascript extension file for a particular backend.""")

    def _get_data(self):
        # Get initial frame to draw immediately
        init_frame = self._plot_figure(0, fig_format='html')
        data = super(BokehWidget, self)._get_data()
        return dict(data, init_frame=init_frame)

    def encode_frames(self, frames):
        if self.export_json:
            self.save_json(frames)
            frames = {}
        else:
            frames = json.dumps(frames).replace('</', r'<\/')
        return frames

    def _plot_figure(self, idx, fig_format='json'):
        """
        Returns the figure in html format on the
        first call and
        """
        state = self.plot.update(idx)
        if self.embed or fig_format == 'html' or old_bokeh:
            return self.renderer.html(self.plot, fig_format)
        else:
            doc = state.document

            if hasattr(doc, 'last_comms_handle'):
                handle = doc.last_comms_handle
            else:
                handle = _CommsHandle(get_comms(doc.last_comms_target),
                                      doc, doc.to_json())
                doc.last_comms_handle = handle

            to_json = doc.to_json()
            if handle.doc is not doc:
                msg = dict(doc=to_json)
            else:
                msg = Document._compute_patch_between_json(handle.json, to_json)
            handle._json = to_json
            handle.comms.send(json.dumps(msg))


class BokehSelectionWidget(BokehWidget, SelectionWidget):
    pass

class BokehScrubberWidget(BokehWidget, ScrubberWidget):
    pass
