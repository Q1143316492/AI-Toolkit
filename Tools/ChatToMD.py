#!/usr/bin/env python311
# -*- coding: utf-8 -*-
"""
Copilot Chat JSON to Markdown Converter
Converts exported Copilot chat JSON to readable Markdown format
"""

import json
import datetime
import re
from typing import Dict, List, Any, Optional

# Constants
MARKDOWN_FILE_EXT = ".md"
JSON_FILE_EXT = ".json"

def LoadJsonFile(szFilePath: str) -> Optional[Dict[str, Any]]:
    """Load JSON file and return parsed data"""
    try:
        with open(szFilePath, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File not found - {szFilePath}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
        return None
    except Exception as e:
        print(f"Error: Failed to load file - {e}")
        return None

def FormatTimestamp(nTimestamp: int) -> str:
    """Convert timestamp to readable format"""
    try:
        dtTime = datetime.datetime.fromtimestamp(nTimestamp / 1000)
        return dtTime.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "Unknown Time"

def ExtractFileName(szFilePath: str) -> str:
    """Extract filename from file path"""
    if not szFilePath:
        return "Unknown File"
    return szFilePath.split('\\')[-1].split('/')[-1]

def ProcessResponsePart(dictPart: Dict[str, Any]) -> str:
    """Process a single response part and return formatted text"""
    szResult = ""
    
    if dictPart.get("kind") == "inlineReference":
        dictRef = dictPart.get("inlineReference", {})
        szName = dictRef.get("name", "Unknown Reference")
        szResult += f"[{szName}]"
    elif dictPart.get("kind") == "codeblockUri":
        dictUri = dictPart.get("uri", {})
        szPath = dictUri.get("fsPath", "")
        szFileName = ExtractFileName(szPath)
        szResult += f"\n\n**File:** `{szFileName}`\n"
    elif dictPart.get("kind") == "toolInvocationSerialized":
        szResult += _ProcessToolInvocation(dictPart)
    elif dictPart.get("value"):
        szValue = dictPart.get("value", "")
        # Handle nested dict in value (like MCP tool calls)
        if isinstance(szValue, dict):
            szResult += _ProcessToolValue(szValue)
        else:
            # Clean up markdown formatting
            szValue = re.sub(r'````\n', '', szValue)
            szResult += szValue
    
    return szResult

def _ProcessToolInvocation(dictTool: Dict[str, Any]) -> str:
    """Process tool invocation and return formatted text"""
    szResult = ""
    
    # Get tool message
    dictInvocationMsg = dictTool.get("invocationMessage", {})
    if isinstance(dictInvocationMsg, dict):
        szMessage = dictInvocationMsg.get("value", "")
    else:
        szMessage = dictInvocationMsg
    
    if szMessage and szMessage != 'Using ""':
        szResult += f"\n**🔧 Tool Call:** {szMessage}\n"    # Get tool parameters/input
    dictToolSpecific = dictTool.get("toolSpecificData", {})
    dictRawInput = dictToolSpecific.get("rawInput", {})
    if dictRawInput:
        # Special handling for SendGmCommandToGame: show formatted GM script directly
        if "szGmScript" in dictRawInput:
            szGmScript = dictRawInput["szGmScript"]
            if isinstance(szGmScript, str) and ("\\n" in szGmScript or "\n" in szGmScript):
                szResult += "**GM Script:**\n```python\n"
                szFormattedScript = szGmScript.replace('\\n', '\n')
                # Remove leading ! if present
                if szFormattedScript.startswith('!'):
                    szFormattedScript = szFormattedScript[1:]
                szResult += szFormattedScript
                szResult += "\n```\n"
            else:
                # Single line GM script, show as parameters
                szResult += "**Parameters:**\n```json\n"
                szResult += json.dumps(dictRawInput, indent=2, ensure_ascii=False)
                szResult += "\n```\n"
        else:
            # Regular tool parameters
            szResult += "**Parameters:**\n```json\n"
            # Convert escaped newlines in parameters for better readability
            dictFormattedInput = {}
            bHasMultilineText = False
            for szKey, szValue in dictRawInput.items():
                if isinstance(szValue, str):
                    dictFormattedInput[szKey] = szValue.replace('\\n', '\n')
                    if "\\n" in szValue or "\n" in szValue:
                        bHasMultilineText = True
                else:
                    dictFormattedInput[szKey] = szValue
            szResult += json.dumps(dictFormattedInput, indent=2, ensure_ascii=False)
            szResult += "\n```\n"
      # Get tool result/output
    dictResultDetails = dictTool.get("resultDetails", {})
    if dictResultDetails:
        listOutput = dictResultDetails.get("output", [])
        bIsError = dictResultDetails.get("isError", False)
        
        if listOutput:
            szResult += "**Output:**\n"
            if bIsError:
                szResult += "⚠️ **Error occurred:**\n"
            
            for dictOutputItem in listOutput:
                if isinstance(dictOutputItem, dict):
                    szOutputValue = dictOutputItem.get("value", "")
                    if szOutputValue:
                        # Convert escaped newlines to real newlines
                        szOutputValue = szOutputValue.replace('\\n', '\n')
                        szResult += f"```\n{szOutputValue}\n```\n"
                else:
                    szOutputStr = str(dictOutputItem)
                    # Convert escaped newlines to real newlines
                    szOutputStr = szOutputStr.replace('\\n', '\n')
                    szResult += f"```\n{szOutputStr}\n```\n"
    
    return szResult

def _ProcessToolValue(dictValue: Dict[str, Any]) -> str:
    """Process tool value dict and return formatted text"""
    szValue = dictValue.get("value", "")
    if szValue:
        return f"*{szValue}*"
    return ""

def ProcessVariables(listVariables: List[Dict[str, Any]]) -> str:
    """Process variable data and return formatted text"""
    if not listVariables:
        return ""
    
    szResult = "**Referenced Files:**\n"
    for dictVar in listVariables:
        if dictVar.get("kind") == "file":
            szName = dictVar.get("name", "Unknown File")
            dictValue = dictVar.get("value", {})
            szPath = dictValue.get("fsPath", "")
            if szPath:
                szResult += f"- `{szName}` - {szPath}\n"
    
    szResult += "\n"
    return szResult

def ConvertChatToMarkdown(dictChatData: Dict[str, Any]) -> str:
    """Convert chat JSON data to Markdown format"""
    szMarkdown = ""
    
    # Header
    szRequester = dictChatData.get("requesterUsername", "Unknown User")
    szResponder = dictChatData.get("responderUsername", "GitHub Copilot")
    
    szMarkdown += f"# Chat Conversation\n\n"
    szMarkdown += f"**Participants:** {szRequester} ↔ {szResponder}\n\n"
    
    # Process requests
    listRequests = dictChatData.get("requests", [])
    for nIndex, dictRequest in enumerate(listRequests, 1):
        # User message
        dictMessage = dictRequest.get("message", {})
        szUserText = dictMessage.get("text", "")
        if szUserText:
            szMarkdown += f"**{nIndex}.** {szUserText}\n\n"
        
        # Variables/Referenced files
        dictVariableData = dictRequest.get("variableData", {})
        listVariables = dictVariableData.get("variables", [])
        szVariableText = ProcessVariables(listVariables)
        if szVariableText:
            szMarkdown += szVariableText
        
        # Response
        listResponse = dictRequest.get("response", [])
        if listResponse:
            szResponseText = ""
            
            for dictPart in listResponse:
                szPartText = ProcessResponsePart(dictPart)
                szResponseText += szPartText
            
            # Clean up response text
            szResponseText = re.sub(r'\n{3,}', '\n\n', szResponseText)
            szResponseText = szResponseText.strip()
            
            if szResponseText:
                szMarkdown += szResponseText + "\n\n"
        
        if nIndex < len(listRequests):
            szMarkdown += "---\n\n"
    
    return szMarkdown

def main():
    """Main function to convert chat JSON to Markdown"""
    szJsonPath = "chat.json"
    szOutputPath = "chat_conversation.md"
    
    print(f"Loading chat data from {szJsonPath}...")
    dictChatData = LoadJsonFile(szJsonPath)
    
    if not dictChatData:
        print("Failed to load chat data!")
        return
    
    print("Converting to Markdown format...")
    szMarkdown = ConvertChatToMarkdown(dictChatData)
    
    print(f"Saving to {szOutputPath}...")
    try:
        with open(szOutputPath, 'w', encoding='utf-8') as file:
            file.write(szMarkdown)
        print(f"Successfully converted chat to {szOutputPath}")
    except Exception as e:
        print(f"Error saving file: {e}")

if __name__ == "__main__":
    main()