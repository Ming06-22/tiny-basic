import math

reserved = ["LET", "PRINT", "INPUT", "IF", "GOTO",
            "SLEEP", "END", "LIST", "REM", "READ",
            "WRITE", "APPEND", "RUN", "CLS", "CLEAR",
            "EXIT", "GOSUB", "RETURN", "GOTOXY",
            "SAVE", "LOAD", "FOR", "TO", "DO", "STEP", "NEXT", "STOP"]

constants = ["PI", "EUL", "TAU", "INF"]

functions = {"ABS": math.fabs, "SIN": math.sin, "ASIN": math.asin, "COS": math.cos, "ACOS": math.acos, "TAN": math.tan,
             "ATAN": math.atan, "SINH": math.sinh, "ASINH": math.asinh, "COSH": math.cosh, "ACOSH": math.acosh,
             "TANH": math.tanh, "ATANH": math.atanh, "LOG1P": math.log1p, "LOG2": math.log2, "LOG10": math.log10,
             "SQRT": math.sqrt, "EXP": math.exp, "DEGREES": math.degrees, "RADIANS": math.radians}

operators = [["==", "!=", ">", "<", ">=", "<="],
             ["."],
             ["<<", ">>"],
             list(functions),
             ["+", "-"],
             ["*", "/", "&", "|", "%"],
             ["^"],
             ["++", "--"],
             list(constants)]

lines = {}
maxLine = 0
linePointer = 0
stopExecution = False
identifiers = {}
printReady = True
returnPos = []
forExpr = {}
forNext = False
forLine = 0
forLinePtr = 0
forStart = 0
forEnd = 0
forStep = 0
forVar = None


def main():
    while True:
        try:
            if printReady:
                print("OK.")
            nextLine = input()
            if len(nextLine) > 0:
                executeTokens(lex(nextLine))
        except KeyboardInterrupt:
            pass
        except SystemExit:
            print("Bye!")
            break
        except:
            print("Execution halted.")


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def getVarType(token):
    if len(token) > 1:
        if token[-1] == "$":
            return "STRING"
    return "NUM"


# Determine whether the customize identifier is valid
def isValidIdentifier(token):
    if len(token) == 0:
        return False
    if len(token) > 1:
        # Identifier may end with $, in this situation need to cut off $
        if token[-1] == "$":
            token = token[0:-1]
    if not (token[0].lower() in "abcdefghijklmnopqrstuvwxyz"):
        return False
    for c in token[1:]:
        if not (c.lower() in "abcdefghijklmnopqrstuvwxyz0123456789"):
            return False
    return True


# Transfer the input line into a list of tokens [content, type]
def lex(line):
    # Determine whether the content is in "" (is a String)
    inString = False
    # Split the input content into single word [content, type]
    tokens = []
    # Temporary store the word which compose of character from each iteration
    currentToken = ""
    # Input line
    line = line + " "
    # Split the line into tokens
    for c in line:
        if not inString and c in " ()\"":
            if len(currentToken) != 0:
                tokens.append([currentToken, "TBD"])
                currentToken = ""
            if c == '"':
                inString = True
        elif inString and c == '"':
            tokens.append([currentToken, "STRING"])
            currentToken = ""
            inString = False
        else:
            currentToken += c
    # Classification tokens
    for token in tokens:
        # Not TBD
        if token[1] != "TBD":
            continue
        # TBD
        value = token[0]
        if is_number(value):
            token[0] = float(token[0])
            token[1] = "NUM"  # Number
        elif value.upper() in reserved:
            token[0] = value.upper()
            token[1] = "RESVD"  # Reserved word
        elif value.upper() == "THEN":
            token[0] = value.upper()
            token[1] = "THEN"
        elif value.upper() == "ELSE":
            token[0] = value.upper()
            token[1] = "ELSE"
        elif value == "=":
            token[1] = "ASGN"
        elif value.upper() in constants:
            token[0] = value.upper()
            token[1] = "CONST"
        elif value.upper() in functions:
            token[0] = value.upper()
            token[1] = "FUNC"
        elif isValidIdentifier(token[0]):
            token[1] = "ID"  # Identifier
        else:
            for i in range(0, len(operators)):
                if token[0] in operators[i]:
                    token[1] = "OP"

    return tokens


def executeTokens(tokens):
    # lines: content of each line (doesn't contain line number)
    global lines, maxLine, stopExecution, linePointer, printReady, identifiers
    global forNext, forExpr, forLine, forLinePtr, forStart, forEnd, forStep, forVar
    printReady = True
    # check whether the first word of a line is line number
    if tokens[0][1] == "NUM":
        lineNumber = int(tokens.pop(0)[0])
        if len(tokens) != 0:
            lines[lineNumber] = tokens
            if lineNumber > maxLine:
                maxLine = lineNumber
        else:
            lines.pop(lineNumber, None)
        printReady = False
        return
    if tokens[0][1] != "RESVD":
        print(f"Error: Unknown command {tokens[0][0]}.")
    else:
        command = tokens[0][0]
        # in FOR_NEXT LOOP
        if forNext:
            # Execute a complete FOR_NEXT LOOP
            if command == "NEXT":
                forNext = False
                while identifiers[forVar][0] <= forEnd:
                    forLinePtr = 0
                    while forLinePtr < forLine:
                        executeTokens(forExpr[forLinePtr])
                        if stopExecution:
                            stopExecution = False
                            return
                        forLinePtr += 1
                    identifiers[forVar][0] += forStep
                forLine = 0
                identifiers.pop(forVar, None)
                forExpr.clear()
            # Special Command
            elif command == "CLS":
                print("\n" * 500)
            elif command == "EXIT":
                quit()
            elif command == "CLEAR":
                maxLine = 0
                lines = {}
                identifiers = {}
            elif command == "RUN" or command == "SAVE":
                print("Error: FOR_NEXT LOOP expects 'NEXT'.")
                return
            elif command == "LOAD":
                if len(tokens) < 2:
                    print("Error: Expected identifier.")
                    return
                lines = {}
                if tokens[1][1] == 'STRING':
                    with open(tokens[1][0], 'rt') as fin:
                        while True:
                            line = fin.readline()
                            print(line[0:-1])
                            if not line:
                                break
                            executeTokens(lex(line[0:-1]))
                else:
                    print("Error: Filename should be a STRING.")
                    return
            # Store the expressions that in FOR_NEXT LOOP
            else:
                forExpr[forLine] = tokens
                forLine += 1
            return
        # Not in FOR_NEXT LOOP
        else:
            if command == "REM":
                return
            elif command == "CLS":
                print("\n" * 500)
            elif command == "END":
                stopExecution = True
            elif command == "EXIT":
                quit()
            elif command == "CLEAR":
                maxLine = 0
                lines = {}
                identifiers = {}
            elif command == "LIST":
                i = 0
                while i <= maxLine:
                    if i in lines:
                        line = str(i)
                        for token in lines[i]:
                            if token[1] == "NUM":
                                tokenVal = getNumberPrintFormat(token[0])
                            elif token[1] == "STRING":
                                tokenVal = f"\"{token[0]}\""
                            else:
                                tokenVal = token[0]
                            line += " " + str(tokenVal)
                        print(line)
                    i = i + 1
            elif command == "PRINT":
                if not (printHandler(tokens[1:])): stopExecution = True
            elif command == "LET":
                if not (letHandler(tokens[1:])): stopExecution = True
            elif command == "INPUT":
                if not (inputHandler(tokens[1:])): stopExecution = True
            elif command == "GOTO":
                if not (gotoHandler(tokens[1:])): stopExecution = True
            elif command == "IF":
                if not (ifHandler(tokens[1:])): stopExecution = True
            elif command == "STOP":
                linePointer = maxLine + 1
            elif command == "RUN":
                linePointer = 0
                while linePointer <= maxLine:
                    if linePointer in lines:
                        executeTokens(lines[linePointer])
                        if stopExecution:
                            stopExecution = False
                            return
                    linePointer = linePointer + 1
            elif command == "GOSUB":
                if not (gosubHandler(tokens[1:])): stopExecution = True
            elif command == "RETURN":
                if not (returnHandler(tokens[1:])): stopExecution = True
            elif command == "GOTOXY":
                if not (gotoxyHandler(tokens[1:])): stopExecution = True
            elif command == "FOR":
                for i in range(len(tokens) - 1, 0, -1):
                    if tokens[i][0] == "DO":
                        if not (forHandler(tokens[1:])): stopExecution = True
                        return
                forHandler(tokens[1:], True)
                forNext = True
            elif command == "SAVE":
                if len(tokens) < 2:
                    print("Error: Expected identifier.")
                    return
                if tokens[1][1] == 'STRING':
                    linePointer = 0
                    file = ""
                    while linePointer <= maxLine:
                        if linePointer in lines:
                            file += str(linePointer) + " "
                            for e in lines[linePointer]:
                                if e[1] == 'STRING':
                                    file += '"' + e[0] + '"'
                                else:
                                    file += str(e[0]) + " "
                            file += '\n'
                            if stopExecution:
                                stopExecution = False
                                return
                        linePointer = linePointer + 1
                    with open(tokens[1][0], 'wt') as fout:
                        fout.write(file)
                else:
                    print("Error: Filename should be a STRING.")
                    return
            elif command == "LOAD":
                if len(tokens) < 2:
                    print("Error: Expected identifier.")
                    return
                lines = {}
                if tokens[1][1] == 'STRING':
                    with open(tokens[1][0], 'rt') as fin:
                        while True:
                            line = fin.readline()
                            print(line[0:-1])
                            if not line:
                                break
                            executeTokens(lex(line[0:-1]))
                else:
                    print("Error: Filename should be a STRING.")
                    return


def getNumberPrintFormat(num):
    if int(num) == float(num):
        return int(num)
    return num


def gotoHandler(tokens):
    global linePointer
    if len(tokens) == 0:
        print("Error: Expected expression.")
        return
    newNumber = solveExpression(tokens, 0)
    if newNumber[1] != "NUM":
        print("Error: Line number expected.")
    else:
        linePointer = newNumber[0] - 1
    return True


def gosubHandler(tokens):
    global linePointer, returnPos
    if len(tokens) == 0:
        print("Error: Expected expression.")
        return
    newNumber = solveExpression(tokens, 0)
    if newNumber[1] != "NUM":
        print("Error: Line number expected.")
    else:
        returnPos.append(linePointer)
        linePointer = newNumber[0] - 1
    return True


def returnHandler(tokens):
    global linePointer, returnPos
    if len(tokens) == 0:
        if len(returnPos) != 0:
            linePointer = returnPos.pop(-1)
        return True
    else:
        print("Malformed return statement.")
        return


def inputHandler(tokens):
    varName = None
    if len(tokens) == 0:
        print("Error: Expected identifier.")
        return
    elif len(tokens) == 1 and tokens[0][1] == "ID":
        varName = tokens[0][0]
    else:
        varName = solveExpression(tokens, 0)[0]
        if not (isValidIdentifier(varName)):
            print(f"Error: {varName} is not a valid identifier.")
            return
    while True:
        print("?", end='')
        varValue = input()
        if getVarType(varName) == "STRING":
            identifiers[varName] = [varValue, "STRING"]
            break
        else:
            if is_number(varValue):
                identifiers[varName] = [varValue, "NUM"]
                break
            else:
                print("Try again.")
    return True


def ifHandler(tokens):
    thenPos = None
    elsePos = None
    for i in range(0, len(tokens)):
        if tokens[i][1] == "THEN":
            thenPos = i
            break
    if thenPos is None:
        print("Error: Malformed IF statement.")
        return
    for i in range(thenPos + 1, len(tokens)):
        if tokens[i][1] == "ELSE":
            elsePos = i
            break
    exprValue = solveExpression(tokens[0:thenPos], 0)
    if exprValue is None:
        return
    elif exprValue[0] != 0:
        if elsePos is None:
            if len(tokens[thenPos:]) == 0:
                print("Error: Malformed IF statement.")
                return
            executeTokens(tokens[thenPos + 1:])
        else:
            if len(tokens[thenPos:elsePos]) == 0 or len(tokens[elsePos:]) == 0:
                print("Error: Malformed IF statement.")
                return
            executeTokens(tokens[thenPos + 1:elsePos])
    else:
        if elsePos is None:
            if len(tokens[thenPos:]) == 0:
                print("Error: Malformed IF statement.")
                return
        else:
            if len(tokens[thenPos:elsePos]) == 0 or len(tokens[elsePos:]) == 0:
                print("Error: Malformed IF statement.")
                return
            executeTokens(tokens[elsePos + 1:])
    return True


def letHandler(tokens):
    varName = None
    varValue = None
    eqPos = None
    for i in range(0, len(tokens)):
        if tokens[i][1] == "ASGN":
            eqPos = i
            break
    if eqPos is None:
        print("Error: Malformed LET statement.")
        return
    if eqPos == 1 and tokens[0][1] == "ID":
        varName = tokens[0][0]
    else:
        if len(tokens[0:i]) == 0:
            print("Error: Expected identifier.")
            return
        varName = solveExpression(tokens[0:i], 0)
        if varName is None:
            stopExecution = True
            return
        varName = varName[0]
        if not (isValidIdentifier(varName)):
            print(f"Error: {varName} is not a valid identifier.")
            return
    if len(tokens[i + 1:]) == 0:
        print("Error: Expected expression.")
        return
    varValue = solveExpression(tokens[i + 1:], 0)
    if varValue is None:
        return
    if getVarType(varName) != varValue[1]:
        print(f"Error: Variable {varName} type mismatch.")
        return
    identifiers[varName] = varValue
    return True


def printHandler(tokens):
    if len(tokens) == 0:
        print("Error: Expected identifier.")
        return
    exprRes = solveExpression(tokens, 0)
    if exprRes is None:
        return
    if exprRes[1] == "NUM":
        exprRes[0] = getNumberPrintFormat(exprRes[0])
    print(exprRes[0])
    return True


def gotoxyHandler(tokens):
    if len(tokens) < 2:
        print("Error: Expected identifier.")
        return
    commaPos = 0
    for token in tokens:
        if "," in str(token[0]):
            break
        commaPos += 1
    if commaPos == len(tokens):
        print("Error: Malformed GOTOXY statement.")
        return
    tokens[commaPos][0] = float(tokens[commaPos][0][:-1])
    if is_number(tokens[commaPos][0]):
        tokens[commaPos][1] = "NUM"
    else:
        tokens[commaPos][1] = "ID"
    row = solveExpression(tokens[0:commaPos + 1], 0)
    column = solveExpression(tokens[commaPos + 1:], 0)
    if row is None or column is None:
        return
    for i in range(int(row[0]) - 1):
        print("")
    for i in range(int(column[0]) - 1):
        print(" ", end="")
    return True


def forHandler(tokens, next=False):
    global forStart, forEnd, forStep, forVar
    toPos = stepPos = doPos = None
    for i in range(0, len(tokens)):
        if tokens[i][0] == "TO":
            toPos = i
            break
    if toPos is None:
        print("Error: Malformed FOR statement.")
        return
    for i in range(toPos + 1, len(tokens)):
        if tokens[i][0] == "STEP":
            stepPos = i
        if tokens[i][0] == "DO":
            doPos = i
            break
    letHandler(tokens[0:toPos])
    if stepPos is not None:
        forStep = tokens[stepPos + 1][0]
    else:
        forStep = 1
    forStart = tokens[toPos - 1][0]
    forEnd = tokens[toPos + 1][0]
    forVar = tokens[0][0]
    identifiers[forVar][0] = forStart
    if not next:
        while identifiers[forVar][0] <= forEnd:
            executeTokens(tokens[doPos + 1:])
            identifiers[forVar][0] += forStep
        identifiers.pop(forVar, None)
    return True


def getIdentifierValue(name):
    return identifiers[name]


# operation
def solveExpression(tokens, level):
    leftSideValues = []
    rightSideValues = []

    if level < len(operators):
        for i in range(0, len(tokens)):
            if not (tokens[i][1] in ["OP", "NUM", "STRING", "ID", "CONST", "FUNC"]):
                print(f"Error: Unknown operand {tokens[i][0]}")
                return None

            if (tokens[i][1] == "OP" or tokens[i][1] == "CONST" or tokens[i][1] == "FUNC") and \
                    tokens[i][0] in operators[level]:
                exprResL = None
                exprResR = None
                if len(leftSideValues) != 0:
                    exprResL = solveExpression(leftSideValues, level)
                rightSideValues = tokens[i + 1:]
                if len(rightSideValues) != 0:
                    exprResR = solveExpression(rightSideValues, level)
                # constant
                if tokens[i][0] in constants:
                    if tokens[i][0] == "PI":
                        return [math.pi, "NUM"]
                    elif tokens[i][0] == "EUL":
                        return [math.e, "NUM"]
                    elif tokens[i][0] == "TAU":
                        return [math.tau, "NUM"]
                    elif tokens[i][0] == "INF":
                        return [math.inf, "NUM"]
                    else:
                        return None
                # math functions
                elif tokens[i][0] in functions:
                    if exprResR is None:
                        print("Error: Functions expects value.")
                        return None
                    elif exprResL is not None:
                        print("Error: Malformed Function statement.")
                        return None
                    elif exprResR[1] != "NUM":
                        print("Error: Operand type mismatch.")
                        return None
                    else:
                        return [functions[tokens[i][0]](exprResR[0]), "NUM"]
                # operators
                else:
                    if exprResL is None or exprResR is None:
                        return None
                    if tokens[i][0] == "+":
                        if exprResL is None or exprResR is None:
                            print("Error: Operator expects value.")
                            return None
                        elif exprResL[1] == "NUM" and exprResR[1] == "NUM":
                            return [float(exprResL[0]) + float(exprResR[0]), "NUM"]
                        else:
                            print("Error: Operand type mismatch.")
                            return None
                    elif tokens[i][0] == "-":
                        if exprResL is None or exprResR is None:
                            print("Error: Operator expects value.")
                            return None
                        elif exprResL[1] == "NUM" and exprResR[1] == "NUM":
                            return [float(exprResL[0]) - float(exprResR[0]), "NUM"]
                        else:
                            print("Error: Operand type mismatch.")
                            return None
                    elif tokens[i][0] == "/":
                        if exprResL is None or exprResR is None:
                            print("Error: Operator expects value.")
                            return None
                        elif exprResL[1] == "NUM" and exprResR[1] == "NUM":
                            return [float(exprResL[0]) / float(exprResR[0]), "NUM"]
                        else:
                            print("Error: Operand type mismatch.")
                            return None
                    elif tokens[i][0] == "*":
                        if exprResL is None or exprResR is None:
                            print("Error: Operator expects value.")
                            return None
                        elif exprResL[1] == "NUM" and exprResR[1] == "NUM":
                            return [float(exprResL[0]) * float(exprResR[0]), "NUM"]
                        else:
                            print("Error: Operand type mismatch.")
                            return None
                    elif tokens[i][0] == "^":
                        if exprResL is None or exprResR is None:
                            print("Error: Operator expects value.")
                            return None
                        elif exprResL[1] == "NUM" and exprResR[1] == "NUM":
                            return [float(exprResL[0]) ** float(exprResR[0]), "NUM"]
                        else:
                            print("Error: Operand type mismatch.")
                            return None
                    elif tokens[i][0] == "%":
                        if exprResL is None or exprResR is None:
                            print("Error: Operator expects value.")
                            return None
                        elif exprResL[1] == "NUM" and exprResR[1] == "NUM":
                            return [float(exprResL[0]) % float(exprResR[0]), "NUM"]
                        else:
                            print("Error: Operand type mismatch.")
                            return None
                    elif tokens[i][0] == "==":
                        if exprResL is None or exprResR is None:
                            print("Error: Operator expects value.")
                            return None
                        else:
                            return [exprResL[0] == exprResR[0], "NUM"]
                    elif tokens[i][0] == "!=":
                        if exprResL is None or exprResR is None:
                            print("Error: Operator expects value.")
                            return None
                        else:
                            return [exprResL[0] != exprResR[0], "NUM"]
                    elif tokens[i][0] == "<=":
                        if exprResL is None or exprResR is None:
                            print("Error: Operator expects value.")
                            return None
                        else:
                            return [exprResL[0] <= exprResR[0], "NUM"]
                    elif tokens[i][0] == "<":
                        if exprResL is None or exprResR is None:
                            print("Error: Operator expects value.")
                            return None
                        else:
                            return [exprResL[0] < exprResR[0], "NUM"]
                    elif tokens[i][0] == ">":
                        if exprResL is None or exprResR is None:
                            print("Error: Operator expects value.")
                            return None
                        else:
                            return [exprResL[0] > exprResR[0], "NUM"]
                    elif tokens[i][0] == ">=":
                        if exprResL is None or exprResR is None:
                            print("Error: Operator expects value.")
                            return None
                        else:
                            return [exprResL[0] >= exprResR[0], "NUM"]
                    elif tokens[i][0] == "&":
                        if exprResL is None or exprResR is None:
                            print("Error: Operator expects value.")
                            return None
                        elif exprResL[1] == "NUM" and exprResR[1] == "NUM":
                            return [(exprResL[0]) and (exprResR[0]), "NUM"]
                        else:
                            print("Error: Operand type mismatch.")
                            return None
                    elif tokens[i][0] == "|":
                        if exprResL is None or exprResR is None:
                            print("Error: Operator expects value.")
                            return None
                        elif exprResL[1] == "NUM" and exprResR[1] == "NUM":
                            return [(exprResL[0]) or (exprResR[0]), "NUM"]
                        else:
                            print("Error: Operand type mismatch.")
                            return None
                    elif tokens[i][0] == ".":
                        if exprResL is None or exprResR is None:
                            print("Error: Operator expects value.")
                            return None
                        else:
                            value1 = exprResL[0]
                            if exprResL[1] == "NUM":
                                value1 = str(getNumberPrintFormat(value1))
                            value2 = exprResR[0]
                            if exprResR[1] == "NUM":
                                value2 = str(getNumberPrintFormat(value2))
                            return [value1 + value2, "STRING"]
                    elif tokens[i][0] == "<<":
                        if exprResL is None or exprResR is None:
                            print("Error: Operator expects value.")
                            return None
                        elif exprResL[1] == "NUM" and exprResR[1] == "NUM":
                            return [float(int(exprResL[0]) << int(exprResR[0])), "NUM"]
                        else:
                            print("Error: Operand type mismatch.")
                    elif tokens[i][0] == ">>":
                        if exprResL is None or exprResR is None:
                            print("Error: Operator expects value.")
                            return None
                        elif exprResL[1] == "NUM" and exprResR[1] == "NUM":
                            return [float(int(exprResL[0]) >> int(exprResR[0])), "NUM"]
                        else:
                            print("Error: Operand type mismatch.")
            else:
                leftSideValues.append(tokens[i])
        return solveExpression(leftSideValues, level + 1)
    else:
        if len(tokens) > 1:
            print("Error: Operator expected.")
            return None
        elif tokens[0][1] == "ID":
            if tokens[0][0] in identifiers:
                return getIdentifierValue(tokens[0][0])
            else:
                print(f"Error: Variable {tokens[0][0]} not initialized.")
                return None
        return tokens[0]


if __name__ == '__main__':
    main()