from PyQt4 import QtCore, QtGui, uic
import math

ITEM_UNKNOWN = 0
ITEM_VARIABLE = 1
ITEM_CLASS = 2
ITEM_FUNCTION = 3

class CodeUIItem(QtGui.QGraphicsItem):
	def __init__(self, uniqueName, parent = None, scene = None):
		super(CodeUIItem, self).__init__(parent, scene)
		self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
		self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
		self.setFlag(QtGui.QGraphicsItem.ItemIsFocusable)
		self.uniqueName = uniqueName
		from db.DBManager import DBManager
		entity = DBManager.instance().getDB().searchFromUniqueName(self.uniqueName)
		self.name = ''
		self.lines = 1
		self.kindName = ''
		self.kind = ITEM_UNKNOWN
		if entity:
			self.name = entity.name()
			self.kindName = entity.kindname()
			metricRes = entity.metric(('CountLine',))
			self.lines = metricRes.get('CountLine',1)
			if not self.lines:
				self.lines = 1
		print('name ', self.name, self.lines, self.kindName)

		kindStr = self.kindName.lower()
		print('kind str', kindStr)
		if kindStr.find('function') != -1:
			self.kind = ITEM_FUNCTION
			self.color = QtGui.QColor(255,218,89)
		elif kindStr.find('attribute') != -1 or kindStr.find('variable') != -1:
			self.kind = ITEM_VARIABLE
			self.color = QtGui.QColor(255,198,217)
		elif kindStr.find('class') != -1:
			self.kind = ITEM_CLASS
			self.color = QtGui.QColor(154,177,209)
		else:
			self.kind = ITEM_UNKNOWN
			self.color = QtGui.QColor(195,195,195)

		self.titleFont = QtGui.QFont('arial', int(self.getRadius() * 0.2) + 8)
		fontMetrics = QtGui.QFontMetricsF(self.titleFont)
		self.fontSize = fontMetrics.size(QtCore.Qt.TextSingleLine, self.name)
		self.displayScore = 0

		self.targetPos = self.pos()	# 用于动画目标

	def setTargetPos(self, pos):
		self.targetPos = pos

	def moveToTarget(self, ratio):
		self.setPos(self.pos()* (1.0-ratio) + self.targetPos * ratio)

	def getKind(self):
		return self.kind

	def getUniqueName(self):
		return self.uniqueName

	def getEntity(self):
		from db.DBManager import DBManager
		return DBManager.instance().getDB().searchFromUniqueName(self.uniqueName)

	def getRadius(self):
		return math.pow(float(self.lines+1), 0.25) * 5

	def boundingRect(self):
		adj = 10
		r = self.getRadius()
		return QtCore.QRectF(-r-adj, -r-adj, r*2 + adj*2, r*2 + adj*2)

	def shape(self):
		r = self.getRadius()
		path = QtGui.QPainterPath()
		path.addEllipse(-r,-r,r*2,r*2)
		return path

	def paint(self, painter, styleOptionGraphicsItem, widget_widget=None):
		#super(CodeUIItem, self).paint(painter, styleOptionGraphicsItem, widget_widget)

		painter.setRenderHint(QtGui.QPainter.Antialiasing)
		painter.setRenderHint(QtGui.QPainter.TextAntialiasing)
		r = self.getRadius()

		trans = painter.worldTransform()
		lod = QtGui.QStyleOptionGraphicsItem().levelOfDetailFromTransform(trans)
		if r * lod > 2:
			painter.setPen(QtCore.Qt.NoPen)
			clr = self.color
			if self.isSelected():
				clr = clr.dark(150)
			painter.setBrush(clr)
			painter.drawEllipse(-r,-r,r*2,r*2)

		if r * lod > 5:
			painter.scale(1.0/lod, 1.0/lod)
			painter.setPen(QtGui.QPen())
			painter.setFont(self.titleFont)
			rect = QtCore.QRectF(self.fontSize.width() * -0.5, self.fontSize.height() * -0.5, self.fontSize.width(), self.fontSize.height())

			# dx = 1.1
			# painter.setPen(QtGui.QPen(QtGui.QColor(255,255,255)))
			# rect0 = rect.translated(dx,dx)
			# painter.drawText(rect0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter, self.name)
			# rect0 = rect.translated(dx,-dx)
			# painter.drawText(rect0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter, self.name)
			# rect0 = rect.translated(-dx,dx)
			# painter.drawText(rect0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter, self.name)
			# rect0 = rect.translated(-dx,-dx)
			# painter.drawText(rect0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter, self.name)

			painter.setPen(QtGui.QPen(QtGui.QColor(0,0,0)))
			painter.drawText(rect, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter, self.name)

	def contextMenuEvent(self, event):
		#print ('context menu')

		from UIManager import UIManager
		UIManager.instance().getScene().clearSelection()
		self.setSelected(True)

		itemMenu = UIManager.instance().getMainUI().getItemMenu()
		itemMenu.exec(event.screenPos())

	def mousePressEvent(self, event):
		super(CodeUIItem, self).mousePressEvent(event)

		self.displayScore += 1

	def mouseDoubleClickEvent(self, event):
		super(CodeUIItem, self).mouseDoubleClickEvent(event)

		from UIManager import UIManager
		scene = UIManager.instance().getScene()
		if scene:
			scene.showInEditor()

	def mouseMoveEvent(self, event):
		super(CodeUIItem, self).mouseMoveEvent(event)
		self.targetPos = QtCore.QPointF(self.pos().x(), self.pos().y())