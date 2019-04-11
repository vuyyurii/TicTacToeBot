import copy
import random
import time


infinity = 1e10

class Team27():

	def __init__(self):
		
		self.start = 0
		self.flag  = ' '
		self.opp_flag =' '
		self.depthlimit = 5
		self.timelimit = 15
		self.is_time_up = 0
		self.trans = {}
		self.move_history = []
		self.opp_move_history = []
		self.bonus_move = 0
		self.opp_bonus_move = 0
		self.weight = [2,3,3,2,3,4,4,3,3,4,4,3,2,3,3,2]

	def move(self, board, old_move, flag):

		self.start = time.time()
		self.flag = flag
		self.is_time_up = 0
		self.trans.clear()
		if self.flag == 'x':
			self.opp_flag = 'o'
		else:
			self.opp_flag = 'x'

		#print "row->", rowstats[0], rowstats[1], rowstats[2], rowstats[3]
		#print "opp_row->", opp_rowstats[0], opp_rowstats[1], opp_rowstats[2], opp_rowstats[3]
		#print "col->", colstats[0], colstats[1], colstats[2], colstats[3]
		#print "opp_col->", opp_colstats[0], opp_colstats[1], opp_colstats[2], opp_colstats[3] 

		prev_block_row = old_move[0]/4
		prev_block_col = old_move[1]/4
		if board.block_status[prev_block_row][prev_block_col] == self.flag:
			self.bonus_move += 1
		elif board.block_status[prev_block_row][prev_block_col] == self.opp_flag:
			self.opp_bonus_move += 1

		possible_moves = board.find_valid_move_cells(old_move)
		if len(possible_moves) == 1:
			return possible_moves[0]
		possible_moves = self.re_order(board, possible_moves, old_move, flag)
		#random.shuffle(possible_moves)
		i = 3
		final_move = possible_moves[0]
		while i<100:
			self.trans.clear()
			self.depthlimit = i
			value, best_move = self.alpha_beta_search(board, old_move, flag, -infinity, infinity, 1)
			if self.is_time_up == 0:
				final_move = best_move
			else:
				break
			i = i + 1

		return final_move


	def alpha_beta_search(self, board, old_move, flag, alpha, beta, depth):

		
		hashval = hash(str(board.board_status))
		if(self.trans.has_key(hashval)):
			bounds = self.trans[hashval]
			if(bounds[0] >= beta):
				return bounds[0],old_move
			if(bounds[1] <= alpha):
				return bounds[1],old_move
			alpha = max(alpha,bounds[0])
			beta = min(beta,bounds[1])

		if flag == self.flag:

			node_value, best_move = self.max_player(board, old_move, flag, alpha, beta, depth)

		elif flag == self.opp_flag:

			node_value, best_move = self.min_player(board, old_move, flag, alpha, beta, depth)

		if(node_value <= alpha):
			self.trans[hashval] = [-infinity,node_value]
		if(node_value > alpha and node_value < beta):
			self.trans[hashval] = [node_value,node_value]
		if(node_value>=beta):
			self.trans[hashval] = [node_value,infinity]

		return node_value, best_move


	def max_player(self, board, old_move, flag, alpha, beta, depth):
			
		possible_moves = board.find_valid_move_cells(old_move)
		possible_moves = self.re_order(board, possible_moves, old_move, flag)
		#random.shuffle(possible_moves)

		node_value = -1*infinity
		best_move = possible_moves[0]
		a = alpha
		trial_board = copy.deepcopy(board.block_status)


		for move in possible_moves:
			if time.time() - self.start >= self.timelimit:
				self.is_time_up = 1
				break
			var1, var2 = board.update(old_move, move, flag)
			term_val = self.is_terminal(board)
			if term_val == infinity:
				node_value = term_val
				best_move = move
				board.block_status = copy.deepcopy(trial_board)
				board.board_status[move[0]][move[1]] = '-'
				break
			elif term_val == -1*infinity:
				board.block_status = copy.deepcopy(trial_board)
				board.board_status[move[0]][move[1]] = '-'
				continue
			elif term_val != 'continue':
				value = term_val
			elif depth >= self.depthlimit:
				value = self.getUtility(board)
			else:
				if var2 == True and self.bonus_move < 2:
					self.bonus_move += 1
					value = self.alpha_beta_search(board, move, self.flag, a, beta, depth+1)[0]
					self.bonus_move -= 1
				else:
					value = self.alpha_beta_search(board, move, self.opp_flag, a, beta, depth+1)[0]

			board.block_status = copy.deepcopy(trial_board)
			board.board_status[move[0]][move[1]] = '-'
			if node_value < value:
				node_value = value
				best_move = move
			a = max(a, value)
			if beta <= node_value:
				break

		return node_value, best_move

	def min_player(self, board, old_move, flag, alpha, beta, depth):

		possible_moves = board.find_valid_move_cells(old_move)
		possible_moves = self.re_order(board, possible_moves, old_move, flag)
		#random.shuffle(possible_moves)
		node_value = infinity
		best_move = possible_moves[0]
		b = beta
		trial_board = copy.deepcopy(board.block_status)

		for move in possible_moves:

			if time.time() - self.start >= self.timelimit:
				self.is_time_up = 1
				break

			var1, var2 = board.update(old_move, move, flag)

			term_val = self.is_terminal(board)

			if term_val == -1*infinity:
				node_value = term_val
				best_move = move
				board.block_status = copy.deepcopy(trial_board)
				board.board_status[move[0]][move[1]] = '-'
				break

			elif term_val == infinity:
				board.block_status = copy.deepcopy(trial_board)
				board.board_status[move[0]][move[1]] = '-'
				continue

			elif term_val != 'continue':
				value = term_val
				
			elif depth >= self.depthlimit:
				value = self.getUtility(board)
			else:
				if var2 == True and self.opp_bonus_move < 2:
					self.opp_bonus_move += 1
					value = self.alpha_beta_search(board, move, self.opp_flag, alpha, b, depth+1)[0]
					self.opp_bonus_move -= 1
				else:
					value = self.alpha_beta_search(board, move, self.flag, alpha, b, depth+1)[0]				

			board.block_status = copy.deepcopy(trial_board)
			board.board_status[move[0]][move[1]] = '-'

			if node_value > value:
				node_value = value
				best_move = move
			b = min(b, value)
			if alpha >= node_value:
				break

		return node_value, best_move


	def is_terminal(self, board):

		flag = self.flag
		opp_flag = self.opp_flag

		if board.find_terminal_state()[0] == opp_flag:
			return -infinity
		elif board.find_terminal_state()[0] == flag:
			return infinity
		elif board.find_terminal_state()[0] == 'NONE':
			small_boards_won = 0
			small_boards_lost = 0
			small_boards_drawn = 0
			for i in xrange(4):
				for j in xrange(4):
					if board.block_status[i][j] == flag:
						small_boards_won += 1
					if board.block_status[i][j] == opp_flag:
						small_boards_lost += 1
					if board.block_status[i][j] == 'd':
						small_boards_drawn += 1
			if small_boards_lost == small_boards_won:
				value = 0
			elif small_boards_won > small_boards_lost:
				value = infinity/2 + 10*(small_boards_won-small_boards_lost)
			else:
				value = -infinity/2 - 10*(small_boards_lost-small_boards_won)
			return value 
		else:
			return 'continue'

	def row_stats(self, board, allowed_block):

		flag = self.flag
		opp_flag = self.opp_flag

		rowstats = []
		opp_rowstats = []
		#print allowed_block[0],allowed_block[1]
		for i in range(4*allowed_block[0], 4*allowed_block[0]+4):
			count = 0
			opp_count = 0
			for j in range(4*allowed_block[1], 4*allowed_block[1]+4):
				if board.board_status[i][j] == flag:
					count = count + 1
				elif board.board_status[i][j] == opp_flag:
					opp_count += 1
			rowstats.append(count)
			opp_rowstats.append(opp_count)

		return rowstats, opp_rowstats

	def column_stats(self, board, allowed_block):

		flag = self.flag
		opp_flag = self.opp_flag

		colstats = []
		opp_colstats = []
		for i in range(4*allowed_block[1], 4*allowed_block[1]+4):
			count = 0
			opp_count = 0
			for j in range(4*allowed_block[0], 4*allowed_block[0]+4):
				if board.board_status[j][i] == flag:
					count += 1
				elif board.board_status[j][i] == opp_flag:
					opp_count += 1	
			colstats.append(count)
			opp_colstats.append(opp_count)

		return colstats, opp_colstats

	def diamonds_stats(self, board, allowed_block):

		flag = self.flag
		opp_flag = self.opp_flag

		dia_stats = []
		opp_dia_stats = []
		x = allowed_block[0]
		y = allowed_block[1]
		count = 0
		opp_count = 0

		if board.board_status[4*x+1][4*y] == flag:
			count += 1
		elif board.board_status[4*x+1][4*y] == opp_flag:
			opp_count += 1 

		if board.board_status[4*x][4*y+1] == flag:
			count += 1
		elif board.board_status[4*x][4*y+1] == opp_flag:
			opp_count += 1

		if board.board_status[4*x+2][4*y+1] == flag:
			count += 1
		elif board.board_status[4*x+2][4*y+1] == opp_flag:
			opp_count += 1

		if board.board_status[4*x+1][4*y+2] == flag:
			count += 1
		elif board.board_status[4*x+1][4*y+2] == opp_flag:
			opp_count += 1

		dia_stats.append(count)
		opp_dia_stats.append(opp_count)
		count = 0
		opp_count = 0

		if board.board_status[4*x+1][4*y+1] == flag:
			count += 1
		elif board.board_status[4*x+1][4*y+1] == opp_flag:
			opp_count += 1 

		if board.board_status[4*x][4*y+2] == flag:
			count += 1
		elif board.board_status[4*x][4*y+2] == opp_flag:
			opp_count += 1

		if board.board_status[4*x+2][4*y+2] == flag:
			count += 1
		elif board.board_status[4*x+2][4*y+2] == opp_flag:
			opp_count += 1

		if board.board_status[4*x+1][4*y+3] == flag:
			count += 1
		elif board.board_status[4*x+1][4*y+3] == opp_flag:
			opp_count += 1	

		dia_stats.append(count)
		opp_dia_stats.append(opp_count)
		count = 0
		opp_count = 0

		if board.board_status[4*x+2][4*y] == flag:
			count += 1
		elif board.board_status[4*x+2][4*y] == opp_flag:
			opp_count += 1 

		if board.board_status[4*x+1][4*y+1] == flag:
			count += 1
		elif board.board_status[4*x+1][4*y+1] == opp_flag:
			opp_count += 1

		if board.board_status[4*x+3][4*y+1] == flag:
			count += 1
		elif board.board_status[4*x+3][4*y+1] == opp_flag:
			opp_count += 1

		if board.board_status[4*x+2][4*y+2] == flag:
			count += 1
		elif board.board_status[4*x+2][4*y+2] == opp_flag:
			opp_count += 1

		dia_stats.append(count)
		opp_dia_stats.append(opp_count)
		count = 0
		opp_count = 0

		if board.board_status[4*x+2][4*y+1] == flag:
			count += 1
		elif board.board_status[4*x+2][4*y+1] == opp_flag:
			opp_count += 1 

		if board.board_status[4*x+1][4*y+2] == flag:
			count += 1
		elif board.board_status[4*x+1][4*y+2] == opp_flag:
			opp_count += 1

		if board.board_status[4*x+3][4*y+2] == flag:
			count += 1
		elif board.board_status[4*x+3][4*y+2] == opp_flag:
			opp_count += 1

		if board.board_status[4*x+2][4*y+3] == flag:
			count += 1
		elif board.board_status[4*x+2][4*y+3] == opp_flag:
			opp_count += 1		

		dia_stats.append(count)
		opp_dia_stats.append(opp_count)

		return dia_stats, opp_dia_stats

	def getUtility(self, board):

		tot_sb_util = 0
		for i in xrange(4):
			for j in xrange(4):
				sb_util = self.small_block_evaluate(board, i, j)
				tot_sb_util += sb_util
		wb_util = self.large_block_evaluate(board)
		total_util = wb_util*120 + tot_sb_util

		return total_util  


	def large_block_evaluate(self, board):
		
		temp_block_status = copy.deepcopy(board.block_status)
		rowstats = [0, 0, 0, 0]
		opp_rowstats = [0, 0, 0, 0]
		colstats = [0, 0, 0, 0]
		opp_colstats = [0, 0, 0, 0]
		dia_stats = [0, 0, 0, 0]
		opp_dia_stats = [0, 0, 0, 0]
		for i in xrange(4):
			for j in xrange(4):
				if temp_block_status[i][j] == self.flag:
					colstats[j] += 1
					rowstats[i] += 1
					if 4*i+j in [1, 4, 6, 9]:
						dia_stats[0] += 1
					elif 4*i+j in [2, 5, 7, 10]:
						dia_stats[1] += 1
					elif 4*i+j in [5, 8, 10, 13]:
						dia_stats[2] += 1
					elif 4*i+j in [6, 9, 11, 14]:
						dia_stats[3] += 1
				elif temp_block_status[i][j] == self.opp_flag:
					opp_colstats[j] += 1
					opp_rowstats[i] += 1
					if 4*i+j in [1, 4, 6, 9]:
						opp_dia_stats[0] += 1
					elif 4*i+j in [2, 5, 7, 10]:
						opp_dia_stats[1] += 1
					elif 4*i+j in [5, 8, 10, 13]:
						opp_dia_stats[2] += 1
					elif 4*i+j in [6, 9, 11, 14]:
						opp_dia_stats[3] += 1

		util = 0
		for i in xrange(4):
			for j in xrange(4):
				if temp_block_status[i][j] == self.flag:
					util += self.weight[4*i+j]
				elif temp_block_status[i][j] == self.opp_flag:
					util -= self.weight[4*i+j]
		return self.block_evaluate(rowstats, opp_rowstats, colstats, opp_colstats, dia_stats, opp_dia_stats, util)



	def small_block_evaluate(self, board, x, y):

		allowed_block = [x, y]
		rowstats, opp_rowstats = self.row_stats(board, allowed_block)
		colstats, opp_colstats = self.column_stats(board, allowed_block)
		dia_stats, opp_dia_stats = self.diamonds_stats(board, allowed_block)
		util = 0
		for i in xrange(4):
			for j in xrange(4):
				if board.board_status[4*x+i][4*y+j] == self.flag:
					util += self.weight[4*i+j]
				elif board.board_status[4*x+i][4*y+j] == self.opp_flag:
					util -= self.weight[4*i+j]
		return self.block_evaluate(rowstats, opp_rowstats, colstats, opp_colstats, dia_stats, opp_dia_stats, util)
		
	def block_evaluate(self, rowstats, opp_rowstats, colstats, opp_colstats, dia_stats, opp_dia_stats, util):
		
		row_chance = [0, 0, 0, 0]
		col_chance = [0, 0, 0, 0]
		dia_chance = [0, 0, 0, 0]
		for i in xrange(4):
			if opp_rowstats[i] != 0 and rowstats[i] != 0:
				row_chance[i] = 0
			elif opp_rowstats[i] == 0:
				row_chance[i] = 5
				for k in range(rowstats[i]):
					row_chance[i] = row_chance[i]*16
			else:
				row_chance[i] = -5
				for k in range(opp_rowstats[i]):
					row_chance[i] = row_chance[i]*16
			if opp_colstats[i] != 0 and colstats[i] != 0:
				col_chance[i] = 0
			elif opp_colstats[i] == 0:
				col_chance[i] = 5
				for k in range(colstats[i]):
					col_chance[i] = col_chance[i]*16
			else:
				col_chance[i] = -5
				for k in range(opp_colstats[i]):
					col_chance[i] = col_chance[i]*16
			if opp_dia_stats[i] != 0 and dia_stats[i] != 0:
				dia_chance[i] = 0
			elif opp_dia_stats[i] == 0:
				dia_chance[i] = 5
				for k in range(dia_stats[i]):
					dia_chance[i] = dia_chance[i]*16
			else:
				dia_chance[i] = -5
				for k in range(opp_dia_stats[i]):
					dia_chance[i] = dia_chance[i]*16
		draw = 0
		for i in xrange(4):
			if row_chance[i] == 0 and col_chance[i] == 0 and dia_chance[i] == 0:
				draw = 1
			else:
				draw = 0
		if draw == 1:
			return 0
		for i in xrange(4):
			util = row_chance[i] + col_chance[i] + dia_chance[i] + util
		return util

	def re_order(self, board, possible_moves, old_move, flag):

		dia = []
		rem = []
		sb_win = []
		sb_lost = []
		result = []
		if old_move == (-1, -1):
			random.shuffle(possible_moves)
			return possible_moves
		allowed_block = [old_move[0]%4, old_move[1]%4]
		for move in possible_moves:
			temp = (move[0]%4)*4 + move[1]%4
			if temp in [1, 4, 6, 9]:
				dia.append(move)
			elif temp in [2, 5, 7, 10]:
				dia.append(move)
			elif temp in [5, 8, 10, 13]:
				dia.append(move)
			elif temp in [6, 9, 11, 14]:
				dia.append(move)
			else:
				rem.append(move)

		random.shuffle(rem)
		random.shuffle(dia)
		result = dia
		result = result + rem
		for move in result:
			trial_board = copy.deepcopy(board)
			a, b = trial_board.update(old_move, move, flag)
			if b == True:
				sb_win.append(move)
				result.remove(move)
		for move in result:
			trial_board = copy.deepcopy(board)
			a, b = trial_board.update(old_move, move, flag)
			if b == True:
				sb_lost.append(move)
				result.remove(move)
			#print "After removing",len(possible_moves)
		result = sb_win + sb_lost + result
		return result
